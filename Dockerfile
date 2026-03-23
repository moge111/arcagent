# ArcAgent Dockerfile
# Security: unprivileged user, immutable config (NemoClaw DAC pattern)

FROM python:3.12-slim AS base

# Install Node.js for Claude CLI
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y --no-install-recommends nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Create unprivileged user (NemoClaw pattern)
RUN groupadd -r arcagent && useradd -r -g arcagent -d /app -s /bin/bash arcagent

WORKDIR /app

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application code
COPY src/ src/
COPY skills/ skills/
COPY config.yaml .

# Lock config as root-owned read-only (NemoClaw's DAC pattern)
RUN chown root:root config.yaml && chmod 444 config.yaml

# Create writable data directory for the agent user
RUN mkdir -p /app/data && chown arcagent:arcagent /app/data

# Switch to unprivileged user
USER arcagent

EXPOSE 8080

CMD ["python", "-m", "arcagent.main"]
