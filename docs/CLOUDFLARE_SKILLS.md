# Cloudflare Skills Integration

This file explains how to connect the local DeepAgents + Ollama agent setup to
Cloudflare’s public skills and MCP server infrastructure:

- Skills repo: https://github.com/cloudflare/skills
- MCP server repo: https://github.com/cloudflare/mcp-server-cloudflare
- Cloudflare agent setup prompt: https://developers.cloudflare.com/agent-setup/prompt.md

## What this means for this repo

This repo already supports a skills-style workflow via `.deepagents/skills/` and
MCP server configuration via `.deepagents/.mcp.json`.

You can treat the Cloudflare skills repo as an additional skill library and pair
it with Cloudflare MCP servers so agents can call Cloudflare APIs, docs, bindings,
builds, and observability tools.

## Install Cloudflare skills

Clone the Cloudflare skills repo into your project:

```bash
# From your project root
mkdir -p .deepagents/skills
git clone https://github.com/cloudflare/skills .deepagents/skills/cloudflare
```

After that, the skills are discoverable from the same directory pattern used by
this repo’s existing integration helpers.

## Cloudflare MCP server repository

The official Cloudflare MCP server implementation lives at:
https://github.com/cloudflare/mcp-server-cloudflare

From that repo:

- Remote `*.mcp.cloudflare.com` endpoints are the public servers.
- A separate Code Mode server in `cloudflare/mcp` gives broad API access via code execution.
- Some clients need `mcp-remote` as a bridge when they don’t support remote MCP directly.

Typical remote server URLs from that repo:

```json
{
  "cloudflare": { "url": "https://mcp.cloudflare.com/mcp" },
  "cloudflare-docs": { "url": "https://docs.mcp.cloudflare.com/mcp" },
  "cloudflare-bindings": { "url": "https://bindings.mcp.cloudflare.com/mcp" },
  "cloudflare-builds": { "url": "https://builds.mcp.cloudflare.com/mcp" },
  "cloudflare-observability": { "url": "https://observability.mcp.cloudflare.com/mcp" }
}
```

If your MCP client only accepts local commands, use `npx mcp-remote ...` entries
instead of raw `url` fields. See the MCP server repo README for exact syntax.

## `.deepagents/.mcp.json` example for this repo

```json
{
  "mcpServers": {
    "cloudflare": {
      "url": "https://mcp.cloudflare.com/mcp"
    },
    "cloudflare-docs": {
      "url": "https://docs.mcp.cloudflare.com/mcp"
    },
    "cloudflare-bindings": {
      "url": "https://bindings.mcp.cloudflare.com/mcp"
    },
    "cloudflare-builds": {
      "url": "https://builds.mcp.cloudflare.com/mcp"
    },
    "cloudflare-observability": {
      "url": "https://observability.mcp.cloudflare.com/mcp"
    }
  }
}
```

OAuth triggers automatically on first Cloudflare tool use.

## Supported agents

These instructions apply to Claude Code, Codex, OpenCode, Windsurf, Cursor,
GitHub Copilot, and compatible MCP clients. For the official per-agent setup
commands, see `https://developers.cloudflare.com/agent-setup/prompt.md`.

## Connect from this repo

You can load Cloudflare skills and MCP metadata from Python using helpers in
`integrations/cloudless_gr_integration.py`, but those helpers currently default
to patterns from a separate `cloudless.gr` project.

For this repo, a lighter integration path is:

1. Use `scripts/setup-cloudflare-skills.sh` to clone the skills repo.
2. Add the MCP JSON above to your agent/client config.
3. Start your local agent/SDK with Cloudflare-aware prompts from the cloned
   skill files under `.deepagents/skills/cloudflare/`.
4. Use `from integrations import get_cloudflare_skills` to inspect installed
   Cloudflare skills from Python.

## Use Cloudflare over Ollama

Use `create_cloudflare_agent(...)` to run a DeepAgent on your local Ollama
backend while also enabling Cloudflare skills and writing `.deepagents/.mcp.json`.

```python
from integrations import create_cloudflare_agent

agent = create_cloudflare_agent(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/path/to/your/project",
    temperature=0.1,
    max_tokens=4096,
    enable_cloudflare_mcp=True,
    mcp_config_path=".deepagents/.mcp.json",
)

result = agent.invoke({
    "messages": "Review auth flow using Cloudflare docs/skills if relevant"
})
```

If `deepagents` is not installed, importing `create_cloudflare_agent` will
raise an `ImportError` with the message `deepagents package is not installed.`.
