---
name: web-research
description: "Search the web, fetch pages, summarize articles, check APIs"
allowed-tools: ["web_fetch", "shell_exec"]
---

# Web Research Skill

When the user wants information from the web:

## Fetch a URL
Use the `web_fetch` tool to retrieve page content, then summarize the key points.

## Search the web
Use `shell_exec` with curl to query search APIs or fetch search engine results:
```bash
curl -s "https://html.duckduckgo.com/html/?q=<query>" | grep -oP '(?<=<a rel="nofollow" class="result__a" href=").*?(?=")'
```

## Check APIs
Use `web_fetch` or `curl` to hit REST APIs and parse JSON responses.

## Guidelines
- Summarize content concisely
- Include source URLs
- Note when information might be outdated
