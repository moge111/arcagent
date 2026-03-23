# Terry — Full Capabilities

## Overview

Terry is an autonomous AI agent running 24/7 on a VPS (Ubuntu, 87.99.135.47). He's powered by Claude Opus via Claude Code Max plan. He communicates through Discord and has a web dashboard. He has full server access with no permission restrictions.

---

## Communication

| Channel | How |
|---------|-----|
| Discord | Responds to every message in the server — just type naturally |
| Slash commands | `/ask` (one-shot), `/chat` (start thread), `/skills` (list skills), `/status` (health check) |
| Mentions | @Terry in any channel for a quick response |
| Dashboard | http://87.99.135.47:8080 — status, skills, logs, conversations |

---

## Core Abilities

### Execute Anything
- Run any shell command — bash, python, node, curl, git, docker, etc.
- Install software with apt, pip, npm
- Full sudo access — can manage system services, packages, firewall, users
- No permission restrictions — `bypassPermissions` mode

### Read & Write Files
- Read any file on the server
- Create, edit, overwrite files anywhere
- Manage directories, permissions, symlinks

### Code & Build
- Write full applications in Python, JavaScript, Bash, or any language
- Create multi-file projects with proper structure
- Run and test code immediately
- Debug errors by reading output and fixing code
- Handle complex, multi-step builds

### Web Access
- Fetch any URL (APIs, documentation, articles, pages)
- Search the web via DuckDuckGo
- Take screenshots of websites using a headless browser (Playwright + Chromium)
- Read JavaScript-rendered pages that simple curl can't handle
- Read tweet content from X/Twitter URLs via FxTwitter API

### Image & Visual Content
- Download images from URLs
- Read text from images using OCR (Tesseract)
- Take website screenshots and read/share them
- Send images and files as Discord attachments

### GitHub Integration
- Create repositories
- Push code, create branches, manage PRs
- Deploy to GitHub Pages
- Clone and work on existing repos
- Manage issues and releases

---

## Memory & Persistence

### Long-Term Memory
- Stores facts, preferences, and context in a JSON file on disk
- Survives restarts and reboots
- Recalls memories automatically when relevant
- Tell him "remember X" and he saves it
- Ask "what do you remember?" to see everything stored

### Conversation History
- Saves all conversations to disk per channel
- Remembers context within a channel (last 10 messages)
- Can reference what was discussed earlier

---

## Process Management

### Background Processes
- Run tasks in the background with nohup or screen
- Start persistent terminal sessions with screen/tmux
- Check on running processes and view their output

### Systemd Services
- Create services that auto-restart on failure
- Services survive VPS reboots
- Full lifecycle management: start, stop, restart, enable, disable
- View logs with journalctl

### Scheduled Tasks
- Create cron jobs for recurring tasks
- Schedule one-time future tasks
- Manage and list existing schedules

---

## Self-Improvement

### Create His Own Skills
- Write new SKILL.md files to add capabilities
- Skills define instructions for specific task types
- Restart to load new skills

### Add His Own Tools
- Edit his Python source code to add new @tool functions
- Tools become available to Claude for automated use
- Can extend his own functionality without human intervention

### Modify His Own Behavior
- Update his system prompt, handlers, formatters
- Change how he processes or responds to messages
- Update the web dashboard
- Edit his CLAUDE.md identity file

### Current Skills
| Skill | What it does |
|-------|-------------|
| server-status | Check CPU, memory, disk, uptime, running services |
| file-manager | Browse, search, create, edit, manage files |
| script-runner | Write and run Python, Bash, Node.js scripts |
| web-research | Search the web, fetch pages, summarize content |
| tweet-reader | Read tweet text and images from X/Twitter URLs |
| process-manager | Manage background processes, cron jobs, systemd services |
| screenshot | Take screenshots of websites with headless browser |
| self-improve | Create new skills, add tools, modify his own code |
| example-summarizer | Summarize text, URLs, or documents |
| example-web-search | Search the web and return results |

### Current Tools
| Tool | What it does |
|------|-------------|
| current_time | Get current UTC date and time |
| web_fetch | Fetch content from any URL |
| shell_exec | Execute any shell command |
| read_file | Read file contents from the server |
| write_file | Write/create files on the server |
| memory_remember | Store a fact in persistent memory |
| memory_recall | Recall facts from persistent memory |

---

## Infrastructure

| Component | Details |
|-----------|---------|
| VPS | Hetzner CPX11, 2GB RAM, 40GB disk, Ubuntu, Ashburn VA |
| IP | 87.99.135.47 |
| User | jarvis (with sudo) |
| Service | systemd (arcagent.service) — auto-restarts, survives reboots |
| Dashboard | http://87.99.135.47:8080 |
| GitHub | https://github.com/moge111/arcagent |
| AI Model | Claude Opus 4.6 via Claude Code Max plan |
| Auth | Claude Code Max tokens — no API keys needed |

---

## What He Can't Do

| Limitation | Workaround |
|-----------|------------|
| Interactive terminal programs (vim, debuggers) | Uses sed, non-interactive flags, his own read/write tools |
| See a GUI running | Takes screenshots with headless browser, reads with OCR |
| Stream real-time data continuously | Uses cron/polling to check periodically |
| Process images sent in Discord | Discord image attachments aren't passed to the CLI — paste URLs or paths instead |
| Unlimited response time | 5 minute timeout per message, 25 tool-use turns max |

---

## Example Things You Can Ask

- "Build me a price tracker that monitors Amazon and alerts me on Discord when something drops"
- "What's the server status?"
- "Read this tweet and build what it describes" (paste URL)
- "Remember that my eBay store name is XYZ"
- "Create a Python script that scrapes product prices from this URL"
- "Deploy a landing page to GitHub Pages"
- "Set up a cron job that checks inventory every hour"
- "Take a screenshot of competitor.com"
- "What do you remember about me?"
- "Create a new skill for tracking eBay listings"
- "Check if my web app is still running"
