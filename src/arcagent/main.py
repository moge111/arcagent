"""ArcAgent entry point — wires all modules together."""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from pathlib import Path

from .config import load_config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("arcagent")


async def run() -> None:
    config_path = Path("config.yaml")
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])

    logger.info("Loading config from %s", config_path)
    config = load_config(config_path)

    # Phase 2: Load skills
    from .skills.loader import load_skills
    from .skills.registry import SkillRegistry
    from .skills.compiler import compile_skills_prompt

    skill_dirs = [Path(d) for d in config.skills.dirs]
    skill_entries = load_skills(skill_dirs, config.skills.limits)
    skill_registry = SkillRegistry(skill_entries, config.skills.entries)
    skills_prompt = compile_skills_prompt(
        skill_registry.get_enabled(),
        char_budget=config.skills.limits.max_skills_prompt_chars,
    )
    logger.info("Loaded %d skills (%d enabled)", len(skill_entries), len(skill_registry.get_enabled()))

    # Phase 3: Build tools
    from .tools.registry import ToolRegistry
    from .tools.builtin import register_builtin_tools

    tool_registry = ToolRegistry()
    register_builtin_tools(tool_registry)
    mcp_server = tool_registry.build_mcp_server()
    logger.info("Registered %d tools", len(tool_registry.list_tools()))

    # Build system prompt
    base_prompt = """You are Terry, an AI assistant running on a VPS (Ubuntu Linux server at 87.99.135.47).
You have full access to the server and can do almost anything.

## Your Capabilities

### Execute anything
- Run any shell command (bash, python3, node, curl, git, docker, etc.)
- Read and write files anywhere on the server
- Install packages with apt, pip, npm
- Create and manage systemd services, cron jobs, background processes

### Persistent Memory
You have a memory system that survives across conversations. USE IT.
- To remember something: write to /home/jarvis/arcagent/data/memory.json using python3:
  python3 -c "import json,os; f='/home/jarvis/arcagent/data/memory.json'; d=json.load(open(f)) if os.path.exists(f) else {}; d['KEY']='VALUE'; json.dump(d,open(f,'w'),indent=2)"
- To recall memories: python3 -c "import json,os; f='/home/jarvis/arcagent/data/memory.json'; print(json.dumps(json.load(open(f)),indent=2) if os.path.exists(f) else '{}')"
- To forget: python3 -c "import json; f='/home/jarvis/arcagent/data/memory.json'; d=json.load(open(f)); d.pop('KEY',None); json.dump(d,open(f,'w'),indent=2)"
- ALWAYS check your memories at the start of conversations about topics you might have stored info on.
- Store things like: user preferences, project details, important facts, past decisions.

### Web Access
- Fetch any URL with curl
- Search the web via DuckDuckGo: curl -s "https://html.duckduckgo.com/html/?q=QUERY"
- Read APIs, documentation, articles

### Long-Running Processes
- Use screen or tmux to run processes that persist: screen -dmS name command
- Use systemd to create services that auto-restart and survive reboots
- Use nohup for simple background tasks: nohup command > /tmp/output.log 2>&1 &
- Use cron for scheduled tasks: (crontab -l; echo "*/5 * * * * command") | crontab -
- Check on background processes: screen -ls, systemctl status name, ps aux | grep name

### Screenshots & Visual Content
- Take screenshots of websites using a headless browser (if installed)
- Read images with OCR: python3 -c "from PIL import Image; import pytesseract; print(pytesseract.image_to_string(Image.open('file.jpg')))"
- Download images from URLs: curl -o /tmp/image.jpg "URL"

### Code & Development
- Write, run, and debug code in Python, Bash, Node.js, and more
- Manage git repos, create projects, deploy apps
- Create full web applications and run them on the server
- Set up databases, APIs, background workers

## Rules
- You are chatting with users via Discord. Be helpful, concise, and proactive.
- When asked to do something, just do it — you have full permissions.
- For long output, summarize the key points instead of dumping raw terminal output.
- If a task will take multiple steps, explain your plan briefly, then execute.
- Always check your persistent memory when relevant context might be stored there.
- When you learn something important about the user or a project, save it to memory.

"""
    system_prompt = base_prompt + skills_prompt
    if config.claude.system_prompt_append:
        system_prompt += "\n\n" + config.claude.system_prompt_append

    # Core engine
    from .core.engine import AgentEngine

    engine = AgentEngine(
        system_prompt=system_prompt,
        mcp_servers={"arcagent": mcp_server} if mcp_server else {},
        allowed_tools=[f"mcp__arcagent__{t['name']}" for t in tool_registry.list_tools()],
        cli_path=config.claude.cli_path,
        max_conversation_ttl=config.claude.max_conversation_ttl,
    )

    # Phase 5: Dashboard
    from .dashboard.app import create_dashboard_app

    dashboard_app = create_dashboard_app(engine, skill_registry, tool_registry, config)

    # Phase 4: Discord bot
    from .discord_bot.bot import ArcAgentBot

    tasks: list[asyncio.Task] = []
    bot = None

    # Start dashboard
    import uvicorn

    dashboard_config = uvicorn.Config(
        dashboard_app,
        host=config.dashboard.host,
        port=config.dashboard.port,
        log_level="warning",
    )
    dashboard_server = uvicorn.Server(dashboard_config)
    tasks.append(asyncio.create_task(dashboard_server.serve()))
    logger.info("Dashboard starting on http://%s:%d", config.dashboard.host, config.dashboard.port)

    # Start Discord bot
    if config.discord.bot_token:
        bot = ArcAgentBot(engine, skill_registry, config, tool_registry=tool_registry)
        tasks.append(asyncio.create_task(bot.start(config.discord.bot_token)))
        logger.info("Discord bot starting...")
    else:
        logger.warning("No Discord bot token configured — bot disabled")

    # Start conversation cleanup loop
    tasks.append(asyncio.create_task(engine.conversations.start_cleanup_loop()))

    # Handle shutdown
    shutdown_event = asyncio.Event()

    def _signal_handler() -> None:
        logger.info("Shutdown signal received")
        shutdown_event.set()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _signal_handler)

    await shutdown_event.wait()

    logger.info("Shutting down...")
    await engine.close_all()
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
