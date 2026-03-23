# ArcAgent

Custom AI agent framework powered by Claude Code Max tokens. Discord bot + web dashboard + extensible skills system.

---

## Prerequisites

- **Python 3.11+**
- **Node.js 22+** (for Claude Code CLI)
- **Claude Code Max plan** (logged in via CLI)
- **Discord bot token** ([create one here](https://discord.com/developers/applications))

---

## Step-by-Step Setup

### 1. Clone and enter the project

```bash
cd /path/to/ai-agent-blueprints/arcagent
```

### 2. Install Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

### 3. Authenticate Claude Code

```bash
claude login
```

Follow the prompts to authenticate with your Max plan. This is what ArcAgent uses for all AI — no API keys needed.

### 4. Create a Discord bot

1. Go to https://discord.com/developers/applications
2. Click **New Application**, name it "ArcAgent"
3. Go to **Bot** tab → click **Reset Token** → copy the token
4. Under **Privileged Gateway Intents**, enable:
   - **Message Content Intent**
   - **Server Members Intent** (optional)
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Create Public Threads`, `Read Message History`, `Use Slash Commands`, `Embed Links`
6. Copy the generated URL and open it to invite the bot to your server

### 5. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env`:
```
ARCAGENT_DISCORD_TOKEN=your_discord_bot_token_here
```

### 6. Install Python dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 7. Run ArcAgent

```bash
python -m arcagent.main
```

You should see:
```
2026-03-22 [arcagent] INFO: Loading config from config.yaml
2026-03-22 [arcagent] INFO: Loaded 2 skills (2 enabled)
2026-03-22 [arcagent] INFO: Registered 2 tools
2026-03-22 [arcagent] INFO: Dashboard starting on http://127.0.0.1:8080
2026-03-22 [arcagent] INFO: Discord bot starting...
2026-03-22 [arcagent] INFO: ArcAgent bot connected as ArcAgent#1234
```

### 8. Test it

- In Discord: type `/ask What is 2 + 2?`
- In browser: open `http://localhost:8080` (or your VPS IP:8080)

---

## VPS Deployment

### Option A: Direct (systemd)

#### 1. SSH into your VPS and clone the project

```bash
ssh user@your-vps-ip
# upload or clone the arcagent folder to your VPS
```

#### 2. Install system dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-venv nodejs npm

# Install Claude CLI
sudo npm install -g @anthropic-ai/claude-code
```

#### 3. Authenticate Claude on the VPS

```bash
claude login
```

#### 4. Set up the project

```bash
cd /home/user/arcagent
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
nano .env  # paste your Discord token
```

#### 5. Update config for VPS

Edit `config.yaml` — change dashboard host to allow remote access:

```yaml
dashboard:
  host: "0.0.0.0"   # listen on all interfaces
  port: 8080
```

#### 6. Create a systemd service

```bash
sudo nano /etc/systemd/system/arcagent.service
```

Paste:
```ini
[Unit]
Description=ArcAgent AI Framework
After=network.target

[Service]
Type=simple
User=user
WorkingDirectory=/home/user/arcagent
EnvironmentFile=/home/user/arcagent/.env
ExecStart=/home/user/arcagent/.venv/bin/python -m arcagent.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace `user` with your actual VPS username and adjust paths if needed.

#### 7. Start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable arcagent
sudo systemctl start arcagent
```

#### 8. Check it's running

```bash
sudo systemctl status arcagent
sudo journalctl -u arcagent -f  # live logs
```

#### 9. Open firewall for dashboard (optional)

```bash
sudo ufw allow 8080/tcp
```

Then visit `http://your-vps-ip:8080` in your browser.

---

### Option B: Docker

#### 1. Install Docker on VPS

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# log out and back in
```

#### 2. Upload project and run

```bash
cd /home/user/arcagent
cp .env.example .env
nano .env  # add your Discord token

docker compose up -d --build
```

#### 3. Check logs

```bash
docker compose logs -f
```

#### 4. Stop/restart

```bash
docker compose down      # stop
docker compose up -d     # start
docker compose restart   # restart
```

---

## Usage

### Discord Commands

| Command | Description |
|---------|-------------|
| `/ask <prompt>` | One-shot question — get a quick answer |
| `/chat <topic>` | Start a persistent conversation thread |
| `/skills` | List all loaded skills and their status |
| `/status` | Show agent health, active sessions, tool count |
| `@ArcAgent <message>` | Mention the bot for a quick one-shot reply |

### Dashboard

Open `http://your-server:8080` to see:
- **Status** — uptime, active sessions, skill/tool counts
- **Skills** — toggle skills on/off with switches
- **Logs** — recent activity log

### Adding Skills

Create a new directory in `skills/` with a `SKILL.md` file:

```
skills/
  my-new-skill/
    SKILL.md
```

SKILL.md format:
```markdown
---
name: my-new-skill
description: "What this skill does"
allowed-tools: ["web_fetch"]
---

# My New Skill

Instructions for the agent on how to use this skill...
```

Restart ArcAgent to pick up new skills.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `claude: command not found` | Run `npm install -g @anthropic-ai/claude-code` |
| Bot doesn't respond to slash commands | Wait 1-2 minutes for Discord to sync commands, or kick and re-invite the bot |
| `No Discord bot token configured` | Check your `.env` file has `ARCAGENT_DISCORD_TOKEN=...` |
| Dashboard not loading | Check `config.yaml` has `host: "0.0.0.0"` for VPS, and firewall allows port 8080 |
| `Permission denied` on credentials | Run `chmod 700 ~/.arcagent && chmod 600 ~/.arcagent/credentials.json` |
