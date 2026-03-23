---
name: server-status
description: "Check server health — CPU, memory, disk, uptime, running processes"
allowed-tools: ["shell_exec"]
---

# Server Status Skill

When the user asks about server health, system status, or resource usage, run these commands:

## Quick Status
```bash
uptime && echo "---" && free -h && echo "---" && df -h / && echo "---" && top -bn1 | head -15
```

## Network
```bash
ip addr show | grep inet && echo "---" && ss -tlnp
```

## Running Services
```bash
systemctl list-units --type=service --state=running
```

Present results in a clean, readable format.
