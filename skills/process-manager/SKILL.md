---
name: process-manager
description: "Manage long-running processes, background tasks, cron jobs, and systemd services"
allowed-tools: ["shell_exec", "write_file", "read_file"]
---

# Process Manager Skill

For running and managing persistent processes on the server.

## Background Processes (quick & temporary)

```bash
# Run something in background
nohup python3 /path/to/script.py > /tmp/script.log 2>&1 &

# Check if running
ps aux | grep script.py

# View output
tail -50 /tmp/script.log

# Kill it
kill $(pgrep -f script.py)
```

## Screen Sessions (persistent terminal sessions)

```bash
# Start a named session running a command
screen -dmS myapp python3 server.py

# List sessions
screen -ls

# View output from a session
screen -S myapp -X hardcopy /tmp/screen_output.txt && cat /tmp/screen_output.txt

# Kill a session
screen -S myapp -X quit
```

## Systemd Services (auto-restart, survive reboots)

Create a service file:
```bash
cat > /etc/systemd/system/myapp.service << 'EOF'
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=jarvis
WorkingDirectory=/home/jarvis/myapp
ExecStart=/usr/bin/python3 app.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# NOTE: systemd commands need sudo
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
```

```bash
# Check status
sudo systemctl status myapp

# View logs
sudo journalctl -u myapp -n 50

# Restart
sudo systemctl restart myapp

# Stop
sudo systemctl stop myapp
```

## Cron Jobs (scheduled tasks)

```bash
# List current cron jobs
crontab -l

# Add a cron job (runs every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/bin/python3 /home/jarvis/script.py >> /tmp/cron.log 2>&1") | crontab -

# Remove all cron jobs
crontab -r
```

## Port Management

```bash
# See what's running on a port
ss -tlnp | grep :8080

# Kill process on a port
fuser -k 8080/tcp
```
