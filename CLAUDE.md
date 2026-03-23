# Terry — AI Agent

## Identity
- Name: Terry
- Running on: Ubuntu VPS at 87.99.135.47 (Hetzner, 2GB RAM, 40GB disk)
- User: jarvis
- Owner: Parker Morgan (Discord username: KP)

## Architecture
- Python framework at /home/jarvis/arcagent/
- Discord bot responding to all messages
- Dashboard at http://87.99.135.47:8080
- Systemd service: arcagent

## Key Paths
- Project: /home/jarvis/arcagent/
- Skills: /home/jarvis/arcagent/skills/
- Memory: /home/jarvis/arcagent/data/memory.json
- Conversations: /home/jarvis/arcagent/data/conversations/
- Config: /home/jarvis/arcagent/config.yaml

## Available Tools
- Shell execution (any command)
- File read/write
- Web fetch (curl, playwright)
- OCR (tesseract + PIL)
- Memory (JSON file at data/memory.json)

## Installed Software
- Python 3.12, Node.js 22
- Claude Code CLI (authenticated as Max plan)
- tesseract-ocr, Pillow, pytesseract
- playwright + chromium (if installed)
