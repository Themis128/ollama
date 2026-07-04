# DeepAgents + Ollama Integration

A robust coding agent system integrating DeepAgents SDK with Ollama, featuring production-ready capabilities and modern terminal interface.

## Features

### Core Capabilities
- ✅ **DeepAgents SDK Integration** - Full access to 8 skills and 4 subagents
- ✅ **Ollama Backend** - Local inference with qwen2.5-coder
- ✅ **Cloudless.gr Context** - Project-aware coding with best practices

### Modern GUI (Terminal-Based)
- ✅ **Box-drawing headers** - Professional terminal interface design
- ✅ **Color-coded status** - Visual success/failure indicators
- ✅ **NLP auto-detection** - Automatic command understanding
- ✅ **Ollama server management** - Start/stop/pull from GUI
- ✅ **Project connection** - Connect and scan projects
- ✅ **Enhanced help** - Organized command reference
- ✅ **Better error handling** - Graceful failure messages
- ✅ **Pull progress display** - Spinner animation for model pulls

### Terminal-Separated Agent Execution
- ✅ **Terminal helper script** - `scripts/ollama-agent-terminal.py` for isolated agent sessions
- ✅ **GUI routing** - General agent execution routed through terminal helper
- ✅ **OS launchers** - `.desktop` (Linux) and `.bat` (Windows) launchers
- ✅ **TTY handling** - Proper terminal I/O with commands (/exit, /clear, /help)
- ✅ **Interactive REPL** - Standalone interactive mode via terminal helper

### Agentic Coding Features
- ✅ **TDD Agent** - Red-Green-Refactor cycle with self-correction
- ✅ **Terminal Agent** - Command execution with output parsing
- ✅ **Sandbox Agent** - Isolated execution with security controls
- ✅ **Orchestrator Agent** - Multi-mode (Architect/Code/Debug) orchestration
- ✅ **Web Agent** - Internet communication and data fetching
- ✅ **Debug Agent** - Log analysis and self-fixing capabilities
- ✅ **Agent Storm** - Parallel multi-agent execution pattern

### Security & Governance
- ✅ **Command Allowlists/Blocklists** - Safe command execution
- ✅ **Audit Logging** - Complete execution tracking
- ✅ **Sandbox Isolation** - Secure execution environment
- ✅ **Rate Limiting** - Responsible API usage

## Quick Start

```bash
# From this repo root
source .venv/bin/activate

# Install dependencies if not already installed
uv pip install -r requirements.txt

# Optional: install Cloudflare skills/MCP wiring
./scripts/setup-cloudflare-skills.sh

# Start Ollama server
ollama serve

# Use the agent directly via Ollama
./scripts/ollama-agent.sh "Write a Python function that returns the Fibonacci sequence up to n."

# Or start the terminal GUI
python3 gui.py
```

## Terminal-Separated Agent Execution

The agent can run in two modes:

### In-Process Mode
Direct execution within the GUI process (legacy):

```python
from gui import AgentGUI
# GUI routes directly via _ask_ollama()
```

### Terminal-Separated Mode (Default)
Agent executes in its own terminal window:

```bash
# GUI routes through terminal helper for all "ask" actions
# Launches: python scripts/ollama-agent-terminal.py --model <model> --url <url> "prompt"

# Direct terminal helper usage:
python3 scripts/ollama-agent-terminal.py --interactive
python3 scripts/ollama-agent-terminal.py "Your prompt here"

# OS launchers:
# Linux: Double-click ollama-agent.desktop
# Windows: Double-click ollama-agent.bat
```

## Usage via Ollama

### Direct Ollama invocation

Use `scripts/ollama-agent.sh` for one-off agent calls through Ollama:

```bash
source .venv/bin/activate
./scripts/ollama-agent.sh "Your prompt here"
```

Environment overrides:

```bash
OLLAMA_MODEL=llama3.1 OLLAMA_URL=http://localhost:11434 ./scripts/ollama-agent.sh "Prompt"
```

### Python usage via Ollama

```python
from integrations import create_ollama_agent, create_cloudflare_agent

# Basic Ollama agent
ollama_agent = create_ollama_agent(model="qwen2.5-coder")
result = ollama_agent.invoke({"messages": "Write a Python function"})

# Cloudflare skills/MCP over Ollama
cloudflare_agent = create_cloudflare_agent(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/path/to/your/project",
    enable_cloudflare_mcp=True,
)
result = cloudflare_agent.invoke({
    "messages": "Review auth flow using Cloudflare docs/skills if relevant"
})
```

### Cloudflare over Ollama

Use the local Ollama backend together with the cloned Cloudflare skills and `.deepagents/.mcp.json`.

```bash
# 1. Install Cloudflare skills
./scripts/setup-cloudflare-skills.sh

# 2. Start Ollama
ollama serve

# 3. Use the agent
./scripts/ollama-agent.sh "Review auth flow using Cloudflare docs/skills if relevant"
```



## Terminal-Separated Agent Helper

The terminal-separated agent helper provides isolated execution:

```bash
# Interactive mode
python3 scripts/ollama-agent-terminal.py --interactive

# One-shot prompt
python3 scripts/ollama-agent-terminal.py "Your prompt here"

# With options
python3 scripts/ollama-agent-terminal.py --model qwen2.5-coder --url http://localhost:11434 "Prompt"

# OS Launchers:
# - Linux: Double-click ollama-agent.desktop
# - Windows: Double-click ollama-agent.bat
```

### Terminal Helper Commands

**Interactive REPL Commands:**
- `/exit` / `/quit` - Exit the agent session
- `/clear` - Clear the terminal screen
- `/help` - Show this help

**Environment Variables:**
- `OLLAMA_MODEL` - Agent model name (default: qwen2.5-coder)
- `OLLAMA_URL` - Ollama server URL (default: http://localhost:11434)
- `PROJECT_PATH` - Project path for context (default: current directory)

## Project Picker

Use the interactive project picker to select your working directory:

```bash
./scripts/project-picker.sh
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `start-ollama.sh` | Start Ollama server |
| `stop-ollama.sh` | Stop Ollama server |
| `start-agent.sh` | Start DeepAgents agent |
| `test-agent.sh` | Test agent functionality |
| `test-project.sh` | Test with selected project |
| `project-picker.sh` | Interactive project selection |
| `ollama-agent.sh` | CLI agent with one-shot or interactive mode |
| `ollama-agent-terminal.py` | Terminal-separated agent helper |

## Documentation

| Document | Purpose |
|----------|---------|
| **[Project Work Guide](PROJECT_WORK_GUIDE.md)** | **How to use this with your projects** |
| [Architecture](docs/ARCHITECTURE.md) | System architecture with diagrams |
| [Workflows](docs/WORKFLOWS.md) | Agent workflow patterns |
| [Integration Guide](docs/INTEGRATION_GUIDE.md) | How to integrate with projects |
| [API Reference](docs/API_REFERENCE.md) | Complete API documentation |
| [Complete Reference](docs/COMPLETE_REFERENCE.md) | 100% implementation coverage |

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed diagrams.

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                            │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Orchestrator Agent                          │
│  - Mode switching (Architect/Code/Debug)                │
│  - Task decomposition                                     │
│  - Multi-agent coordination                              │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌─────────────────┐ ┌───────────────┐ ┌────────────────┐
│   Agent Storm   │ │  TDD Agent    │ │  Web Agent     │
│  (Parallel)     │ │  (Tests)      │ │  (Research)    │
└─────────────────┘ └───────────────┘ └────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Terminal + Sandbox                          │
│  - Command execution with security                      │
│  - Output parsing                                       │
│  - Self-correction                                      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              DeepAgents SDK + Ollama                     │
│  - Project context (cloudless.gr)                       │
│  - Skills (8 available)                                 │
│  - Subagents (4 specialized)                            │
└─────────────────────────────────────────────────────────┘
```

## Project Integration

### cloudless.gr
- 8 Skills: code-review, database, deploy, git-workflow, monitoring, performance, security, test
- 4 Subagents: backend-dev, frontend-dev, devops, general-purpose
- 12 MCP Servers: github, git, filesystem, memory, sentry, etc.
- Framework: Next.js 16 + TypeScript + DynamoDB + AWS

### DeepAgents SDK
- Full API access
- Middleware support
- Sub-agent spawning
- Filesystem operations

## Requirements

- Python 3.11+
- Ollama local or remote server
- Dependencies from `requirements.txt`

Install dependencies from this repo root:

```bash
source .venv/bin/activate
uv pip install -r requirements.txt
```

## Project Targets

This repo provides agents, not a fixed project template.

`cloudless.gr` is an example target project used in docs and defaults. To use it,
clone it separately and connect via `PROJECT_PATH` or configuration.

If you point agents at another repo, keep the same `.deepagents/skills/` and
`.deepagents/.mcp.json` conventions in that target project.

## Security

- All dangerous commands blocked by default
- Command allowlist enforced
- Audit logging enabled
- Sandbox isolation optional
- Rate limiting for web requests

## Next Steps

1. Start Ollama: `ollama serve`
2. Use the interactive CLI backend: `./scripts/ollama-agent.sh --interactive`
3. Use the terminal GUI backend: `python3 gui.py`
4. Test with your projects using `project-picker.sh`
5. Configure custom skills in `.deepagents/skills/`
6. Add more MCP servers in `.deepagents/.mcp.json`
7. Install Cloudflare skills: `./scripts/setup-cloudflare-skills.sh`
8. See `docs/CLOUDFLARE_SKILLS.md` for MCP config examples
9. See `docs/OLLAMA_BACKEND.md` for step-by-step instructions for both Ollama implementations

## License

MIT
