# Ollama Backend Documentation

This document explains how to use the local Ollama-backed agent in this repo.

Two implementations are supported:
- Separated terminal helper: `scripts/ollama-agent.sh` running `scripts/ollama-agent-terminal.py`
- Terminal GUI backend: `python gui.py`

## Prerequisites

- Ollama installed and available on PATH
- A model pulled, for example `ollama pull qwen2.5-coder`
- Virtual environment activated: `source .venv/bin/activate`
- Optional Cloudflare skills installed: `./scripts/setup-cloudflare-skills.sh`

## Implementation 1: Separated terminal helper

This is a dedicated separate terminal experience for Ollama-backed agent usage.

Source files:
- `scripts/ollama-agent.sh`
- `scripts/ollama-agent-terminal.py`

### Step 1: Start Ollama

```bash
ollama serve
```

In another shell, verify:

```bash
curl http://localhost:11434/api/tags
```

### Step 2: Install Python dependencies

```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Step 3: Open the separated terminal helper

```bash
./scripts/ollama-agent.sh
```

This starts its own terminal agent session backed by your local Ollama server.

### Step 4: Use the helper terminal

- Type any prompt and press Enter.
- `/exit` or `/quit` leaves the session.
- `/help` shows inline help.
- `/reload` rebuilds the agent in that terminal.

### Step 5: Override model / base URL / project path / cloudflare context

Environment variables:
- `OLLAMA_MODEL=llama3.1`
- `OLLAMA_URL=http://localhost:11434`
- `PROJECT_PATH=/path/to/project`
- `USE_CLOUDFLARE=true`

Example:
```bash
USE_CLOUDFLARE=true OLLAMA_MODEL=llama3.1 ./scripts/ollama-agent.sh
```

## Implementation 2: Terminal GUI backend with `python gui.py`

The GUI now routes general natural-language prompts through the Ollama backend by default.

### Step 1: Start Ollama

```bash
ollama serve
```

### Step 2: Install Python dependencies

```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Step 3: Start the GUI

```bash
python gui.py
```

### Step 4: Use system commands

These still behave as system/project commands:
- `start ollama`
- `stop ollama`
- `pull [model]`
- `list models`
- `connect [path]`
- `scan projects`
- `analyze codebase`
- `check for issues`
- `create API endpoint`
- `add component`
- `build function`

### Step 5: Send general prompts to Ollama

Any unrecognized input is sent through the local Ollama agent.

Examples:
- `Write a Python function that returns the Fibonacci sequence`
- `Review auth flow using Cloudflare docs/skills if relevant`
- `Explain how the orchestrator is wired`

Explicit shortcuts also work:
- `ask Write a Python function...`
- `chat Review auth flow...`

Under the hood, the GUI:
1. Parses the input with NLP.
2. If it matches a known command, runs the original command path.
3. Otherwise, calls `create_ollama_agent(...)` or `create_cloudflare_agent(...)`.
4. Prints the agent response in the terminal.

## Environment variables

- `OLLAMA_MODEL` - model name, default `qwen2.5-coder`
- `OLLAMA_URL` - Ollama server URL, default `http://localhost:11434`
- `PROJECT_PATH` - project path for context
- `PROJECT_NAME` - project name
- `PROJECT_TYPE` - project type
- `USE_CLOUDFLARE` - enable Cloudflare-aware agent context in `scripts/ollama-agent.sh`, default `false`

## Cloudflare skills / MCP

If you want the GUI or shell path to use Cloudflare skills:
1. Run `./scripts/setup-cloudflare-skills.sh`
2. Use `create_cloudflare_agent(...)` in Python.
3. In the separated terminal helper, set `USE_CLOUDFLARE=true`.

The local `.deepagents/.mcp.json` contains the Cloudflare MCP server config written by `write_cloudflare_mcp_config(...)`.

## Troubleshooting

- If `python gui.py` exits immediately, check dependency installation and deepagents availability.
- If `scripts/ollama-agent.sh` hangs, confirm `ollama serve` is running and the model is pulled.
- If Cloudflare skills are not found, run `./scripts/setup-cloudflare-skills.sh`.
- If `scripts/ollama-agent.sh` cannot import integrations, confirm the virtual environment is activated.

## Source files

- `scripts/ollama-agent.sh`
- `scripts/ollama-agent-terminal.py`
- `integrations/deepagents_ollama.py`
- `integrations/cloudless_gr_integration.py`
- `gui.py`
- `docs/CLOUDFLARE_SKILLS.md`
