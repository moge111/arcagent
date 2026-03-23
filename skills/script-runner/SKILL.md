---
name: script-runner
description: "Write and run Python, Bash, or Node.js scripts on the server"
allowed-tools: ["shell_exec", "write_file", "read_file"]
---

# Script Runner Skill

When the user wants to run code or automate tasks:

## Python scripts
1. Write the script to a temp file using `write_file`
2. Run it with `python3 /tmp/script.py`

## Bash scripts
1. Write the script to a temp file
2. Run with `bash /tmp/script.sh`

## Node.js scripts
1. Write the script to a temp file
2. Run with `node /tmp/script.js`

## Quick one-liners
- Python: `python3 -c "print('hello')"`
- Bash: direct `shell_exec`
- Node: `node -e "console.log('hello')"`

Always show the script content and output to the user.
