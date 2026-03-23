---
name: example-summarizer
description: "Summarize text content, URLs, or documents into concise bullet points"
allowed-tools: ["web_fetch"]
---

# Summarizer Skill

When the user asks to summarize content, use this skill.

## Usage
- For URLs: fetch the content using the `web_fetch` tool, then summarize
- For text: summarize the provided text directly
- Output as concise bullet points unless otherwise requested

## Output Format
- Use markdown bullet points
- Keep summaries to 3-5 key points
- Include the source URL if applicable
