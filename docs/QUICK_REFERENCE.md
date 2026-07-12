# Quick Reference Guide

Fast reference for common operations in the DeepAgents + Ollama integration.

## 🚀 Quick Start

```bash
# 1. Install dependencies
source .venv/bin/activate
uv pip install -r requirements.txt

# 2. Start Ollama
./scripts/start-ollama.sh
# or: ollama serve

# 3. Start GUI
python3 gui.py
```

## 📦 Python Imports

```python
# All-in-one import
from integrations import (
    # Agents
    TDDAgent, TerminalAgent, SandboxAgent, Orchestrator, 
    WebAgent, DebugAgent, AgentStorm, AgentRole,
    # Base
    create_ollama_agent, create_cloudless_agent, create_cloudflare_agent,
    # Tools
    ClineAdapter, NLPProcessor,
)
```

## 🔧 Common Operations

| Task | Agent | Method |
|------|-------|--------|
| Create feature | TDDAgent | `agent.run_tdd(feature, test_file, impl_file)` |
| Run command | TerminalAgent | `agent.execute("command")` |
| Secure execute | SandboxAgent | `agent.execute("command")` |
| Research topic | WebAgent | `agent.research("topic")` |
| Search web | WebAgent | `agent.search("query")` |
| Fetch URL | WebAgent | `agent.fetch("url")` |
| Multi-perspective | AgentStorm | `agent.storm(task, prompt)` |
| Orchestrate task | Orchestrator | `agent.execute(task, mode="auto")` |
| Analyze error | DebugAgent | `agent.analyze_error(error, file_path)` |

## 🖥️ GUI Commands

| Category | Commands |
|----------|----------|
| **Development** | `Create a new [feature]`, `Implement [functionality] with tests`, `Add [feature] to [module]` |
| **Testing** | `Run tests`, `Run tests and fix failures`, `Run build`, `Check for errors` |
| **Analysis** | `Analyze codebase`, `Check for issues`, `Review code` |
| **Code Gen** | `Create API endpoint`, `Add component`, `Build function` |
| **Research** | `Research [topic]`, `Find documentation for [API]`, `Search for [query]` |
| **Ollama** | `start ollama`, `stop ollama`, `check ollama`, `pull [model]`, `list models` |
| **Project** | `connect [path]`, `scan projects`, `current` |
| **System** | `help`, `history`, `clear`, `project`, `exit` |

## 🌐 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `qwen2.5-coder` | Default model |
| `PROJECT_PATH` | Current directory | Target project path |
| `PROJECT_TYPE` | Auto-detected | Project type |
| `PROJECT_NAME` | Auto-detected | Project name |

## 🛡️ Security - Blocklisted Commands

| Category | Commands |
|----------|----------|
| **Deletion** | `rm -rf`, `rm -r`, `rm -f` |
| **Disk** | `mkfs`, `dd`, `fdisk`, `parted` |
| **Permissions** | `chmod 777`, `chown`, `chmod +s` |
| **Privilege** | `sudo`, `su -`, `pkexec` |
| **Network** | `netcat`, `nc -`, `ncat` |
| **Encoding** | `base64 -d`, `xxd -r` |
| **Execution** | `exec`, `eval`, `source`, `bash -c`, `sh -c` |

## 🎭 Orchestrator Modes

| Mode | When to Use |
|------|-------------|
| `auto` | Complete end-to-end workflow (default) |
| `architect` | System design and planning |
| `code` | Implementation and refactoring |
| `debug` | Error fixing and analysis |
| `orchestrator` | Multi-step coordination |

## 👥 Agent Storm Roles

| Role | Focus |
|------|-------|
| `architect` | System design and architecture |
| `backend` | API, database, business logic |
| `frontend` | UI components and user experience |
| `security` | Security vulnerabilities and best practices |
| `testing` | Test coverage and quality |
| `devops` | Infrastructure and deployment |

## 📡 MCP Tools (Cloudflare)

| Tool | Purpose |
|------|---------|
| `cf_agent_status` | Check CF CodingAgent state |
| `cf_agent_run` | Send task to CF CodingAgent |
| `cf_agent_review_with_ollama` | Review CF result with Ollama |
| `cf_agent_full_loop` | Run + review in one call |
| `cf_agent_apply_patch` | Apply patch to repository |

## 🔌 ClineAdapter Tools

| Tool | Parameters | Returns |
|------|------------|---------|
| `list_files` | `path`, `max_depth` | `files` list |
| `read_file` | `path` | `content`, `lines` |
| `write_file` | `path`, `content` | `bytes_written` |
| `run_command` | `command`, `cwd`, `timeout` | `stdout`, `stderr` |
| `ask_agent` | `prompt`, `model`, `url` | `response` |
| `list_models` | `url` | `models` list |
| `pull_model` | `model` | `stdout` |
| `check_ollama` | `url` | `status` |
| `search_files` | `pattern`, `directory` | `matches` |
| `get_file_info` | `path` | `size`, `modified`, etc. |
| `analyze_code` | `path`, `focus` | `file_types`, `total_files` |
| `generate_test` | `path`, `framework` | `test_file` path |

## 📋 File Patterns

| Pattern | Project Type |
|---------|--------------|
| `package.json` | Node.js / Next.js |
| `pyproject.toml` | Python (modern) |
| `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pom.xml` | Java/Maven |
| `build.gradle` | Java/Gradle |
| `.git` | Git repository |
| `.deepagents` | DeepAgents project |

## 🔤 NLP Intent Patterns

| Intent | Patterns | Weight |
|--------|----------|--------|
| `ANALYZE` | `analyze`, `review`, `check`, `assess` | 0.9 |
| `ANALYZE` | `codebase`, `quality`, `issues` | 0.8 |
| `CODE` | `create`, `add`, `build`, `implement` | 0.9 |
| `CODE` | `api`, `endpoint`, `function`, `component` | 0.7 |
| `TEST` | `test`, `spec`, `unit`, `e2e` | 0.9 |
| `TEST` | `run test`, `fix test` | 0.95 |
| `RESEARCH` | `research`, `find documentation` | varies |
| `OLLAMA` | `start ollama`, `pull model` | varies |

## ⚙️ Configuration Defaults

### TDDAgent
```python
TDDConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/home/tbaltzakis/cloudless.gr",
    temperature=0.1,
    max_iterations=10,
    timeout=60,
)
```

### Orchestrator
```python
OrchestratorConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/home/tbaltzakis/cloudless.gr",
    temperature=0.1,
    max_modes=5,
)
```

### AgentStorm
```python
AgentStormConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    num_agents=4,
    max_workers=4,
    timeout=300,
)
```

### WebAgent
```python
WebConfig(
    rate_limit=10,  # requests per minute
    timeout=30,
    cache_dir="/tmp/web_agent_cache",
    safe_domains=["docs.langchain.com", "nextjs.org", ...],
)
```

## 📜 Scripts

| Script | Command |
|--------|---------|
| Start Ollama | `./scripts/start-ollama.sh` |
| Stop Ollama | `./scripts/stop-ollama.sh` |
| Test agent | `./scripts/test-agent.sh` |
| Pick project | `./scripts/project-picker.sh` |
| CLI prompt | `./scripts/ollama-agent.sh "prompt"` |
| Terminal helper | `python3 scripts/ollama-agent-terminal.py` |
| Interactive helper | `python3 scripts/ollama-agent-terminal.py --interactive` |
| Setup Cloudflare | `./scripts/setup-cloudflare-skills.sh` |
| Debug Ollama | `./scripts/debug-ollama.sh` |

## 🎨 CLI Quick Examples

```bash
# One-shot via shell
./scripts/ollama-agent.sh "Create a Python function for fibonacci"

# Python interactive
python3 scripts/ollama-agent-terminal.py --interactive

# Cline adapter test
python -m integrations.cline_adapter --tool list_files --params '{"max_depth": 2}'

# NLP processor test
python scripts/test-nlp-processor.py

# Validate workflows
python scripts/validate-workflows.py
```

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview & quick start |
| `PROJECT_WORK_GUIDE.md` | Comprehensive usage guide |
| `docs/CODEBASE_INDEX.md` | This file - quick reference |
| `docs/API_REFERENCE.md` | Full API documentation |
| `docs/ARCHITECTURE.md` | System architecture diagrams |
| `docs/WORKFLOWS.md` | Agent workflow patterns |
| `docs/INTEGRATION_GUIDE.md` | Integration instructions |
| `docs/OLLAMA_BACKEND.md` | Ollama setup guide |
| `docs/CLOUDFLARE_SKILLS.md` | Cloudflare skills/MCP config |