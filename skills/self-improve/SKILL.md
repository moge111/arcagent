---
name: self-improve
description: "Create new skills, add tools, update your own code, and reload"
allowed-tools: ["shell_exec", "write_file", "read_file"]
---

# Self-Improvement Skill

You can modify yourself — add skills, add tools, update your own source code.

## Creating a new skill

1. Create a directory in /home/jarvis/arcagent/skills/
2. Write a SKILL.md file with YAML frontmatter and instructions

```bash
mkdir -p /home/jarvis/arcagent/skills/my-new-skill
```

SKILL.md format:
```markdown
---
name: my-new-skill
description: "What this skill does"
allowed-tools: ["shell_exec"]
---

# My New Skill
Instructions for how to use this skill...
```

## Adding a new tool

Tools are Python functions in /home/jarvis/arcagent/src/arcagent/tools/builtin.py

To add a new tool:

1. Read the current file:
```bash
cat /home/jarvis/arcagent/src/arcagent/tools/builtin.py
```

2. Add a new tool function BEFORE the `register_builtin_tools` function. Follow this pattern:
```python
@tool(
    "tool_name",
    "Description of what the tool does",
    {"param1": str, "param2": int},
)
async def tool_name(args: dict[str, Any]) -> dict[str, Any]:
    param1 = args.get("param1", "")
    # ... tool logic ...
    return {"content": [{"type": "text", "text": "result"}]}
```

3. Register it by adding `registry.register(tool_name)` inside the `register_builtin_tools` function.

4. Restart to load: `sudo systemctl restart arcagent`

## Modifying your own source code

Key files you can edit:
- /home/jarvis/arcagent/src/arcagent/tools/builtin.py — your tools
- /home/jarvis/arcagent/src/arcagent/main.py — startup and system prompt
- /home/jarvis/arcagent/src/arcagent/core/engine.py — how you process messages
- /home/jarvis/arcagent/src/arcagent/discord_bot/handlers.py — how you handle Discord messages
- /home/jarvis/arcagent/src/arcagent/discord_bot/formatters.py — how you format responses
- /home/jarvis/arcagent/src/arcagent/dashboard/ — the web dashboard
- /home/jarvis/arcagent/CLAUDE.md — your persistent identity/context

## After any changes

Always restart to load changes:
```bash
sudo systemctl restart arcagent
```

This briefly disconnects from Discord (~5 seconds) then reconnects automatically.

## Listing current skills and tools

```bash
ls /home/jarvis/arcagent/skills/
for d in /home/jarvis/arcagent/skills/*/; do echo "=== $(basename $d) ==="; head -3 "$d/SKILL.md" 2>/dev/null; echo; done
```

```bash
grep '@tool(' /home/jarvis/arcagent/src/arcagent/tools/builtin.py
```

## Safety rules
- Always read a file before editing it
- Make backups before major changes: `cp file file.bak`
- Test changes work after restart by checking: `sudo systemctl status arcagent`
- If you break yourself, Parker can fix you by uploading code from GitHub
