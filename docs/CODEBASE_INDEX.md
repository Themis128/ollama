# Codebase Index

Complete index of all modules, scripts, and documentation in the DeepAgents + Ollama integration.

## 🏗️ Project Structure

```
ollama/
├── gui.py                          # Main terminal GUI entry point
├── requirements.txt                 # Python dependencies
├── README.md                        # Project overview
├── PROJECT_WORK_GUIDE.md            # Comprehensive usage guide
├── deepagents-ollama.code-workspace # VS Code workspace config
├── pyrightconfig.json               # TypeScript/Python typing config
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md            # System architecture diagrams
│   ├── WORKFLOWS.md               # Agent workflow patterns
│   ├── INTEGRATION_GUIDE.md       # Integration instructions
│   ├── API_REFERENCE.md           # API documentation
│   ├── COMPLETE_REFERENCE.md      # Full implementation coverage
│   ├── CLOUDFLARE_SKILLS.md       # Cloudflare skills/MCP config
│   ├── OLLAMA_BACKEND.md          # Ollama setup guide
│   └── CODEBASE_INDEX.md          # This file
│
├── mcp_server/                    # MCP server implementations
│   └── coding_agent.py            # Cloudflare + Ollama MCP tools (5 tools)
│
├── integrations/                  # Core agent modules
│   ├── __init__.py              # Package exports
│   │
│   ├── deepagents_ollama.py     # Base Ollama integration (DeepAgents SDK)
│   ├── cline_adapter.py         # Cline-compatible tool interface (11 tools)
│   ├── nlp_processor.py         # NLP command parsing with confidence scoring
│   │
│   ├── tdd_agent.py             # Test-Driven Development agent
│   ├── terminal_agent.py        # Terminal command execution
│   ├── sandbox_agent.py         # Secure isolated execution
│   ├── orchestrator_agent.py    # Multi-agent mode orchestration
│   ├── web_agent.py             # Internet research & data fetching
│   ├── debug_agent.py           # Log analysis & self-fixing
│   ├── agent_storm.py           # Parallel multi-agent execution
│   │
│   ├── custom_tools.py          # Tool registry & custom tool framework
│   └── cloudless_gr_integration.py # cloudless.gr project integration
│
└── scripts/                     # Utility scripts
    ├── start-ollama.sh           # Start Ollama server
    ├── stop-ollama.sh            # Stop Ollama server
    ├── start-agent.sh            # Start DeepAgents agent
    ├── test-agent.sh             # Test agent functionality
    ├── project-picker.sh         # Interactive project selection
    ├── ollama-agent.sh           # CLI agent one-shot command
    │
    ├── ollama-agent-terminal.py  # Terminal-separated agent helper
    ├── ollama-agent.desktop      # Linux OS launcher
    ├── ollama-agent.bat          # Windows OS launcher
    │
    ├── debug-ollama.sh           # Debug Ollama integration
    ├── setup-cloudflare-skills.sh # Install Cloudflare skills/MCP
    ├── integrate-cloudless.sh      # Full cloudless.gr integration
    ├── full-integrate.sh         # Complete setup script
    │
    ├── logs-live.py              # Live log monitoring
    ├── logs-live.sh              # Live log monitoring (shell)
    │
    ├── review-cloudflare-result-with-ollama.py # Ollama review of CF results
    ├── test-nlp-processor.py     # NLP processor test
    ├── test-cline-adapter.py     # Cline adapter test
    └── validate-workflows.py     # Workflow validation script
```

## 🔧 Core Integrations

| Module | Description | Key Classes/Functions |
|--------|-------------|----------------------|
| `deepagents_ollama.py` | Base DeepAgents + Ollama bridge | `create_ollama_agent()`, `OllamaConfig`, `ChatOllama` |
| `cline_adapter.py` | Cline-compatible tool interface | `ClineAdapter` (11 tools) |
| `nlp_processor.py` | Natural language command parsing | `NLPProcessor`, `ParsedIntent`, `Intent` |
| `custom_tools.py` | Tool registry framework | `create_tool()`, `ToolRegistry`, `Tool` |

## 🤖 Agent Modules

| Module | Description | Key Classes/Functions |
|--------|-------------|----------------------|
| `tdd_agent.py` | Test-Driven Development cycle | `TDDAgent`, `TDDConfig` |
| `terminal_agent.py` | Shell command execution | `TerminalAgent`, `TerminalConfig` |
| `sandbox_agent.py` | Secure isolated execution | `SandboxAgent`, `SandboxConfig` |
| `orchestrator_agent.py` | Multi-agent orchestration | `Orchestrator`, `OrchestratorConfig`, `AgentMode` |
| `web_agent.py` | Internet research | `WebAgent`, `WebConfig` |
| `debug_agent.py` | Log analysis & fixing | `DebugAgent`, `DebugConfig` |
| `agent_storm.py` | Parallel agent execution | `AgentStorm`, `AgentRole`, `AgentStormConfig` |

## 📡 MCP Server Tools

| Tool | Description | Location |
|------|-------------|----------|
| `cf_agent_status` | Check Cloudflare CodingAgent state | `mcp_server/coding_agent.py` |
| `cf_agent_run` | Send task to CF CodingAgent | `mcp_server/coding_agent.py` |
| `cf_agent_review_with_ollama` | Review CF result with Ollama | `mcp_server/coding_agent.py` |
| `cf_agent_full_loop` | Run + review in one call | `mcp_server/coding_agent.py` |
| `cf_agent_apply_patch` | Apply patch to repository | `mcp_server/coding_agent.py` |

## 🖥️ Scripts

| Script | Purpose |
|--------|---------|
| `start-ollama.sh` | Start Ollama server |
| `stop-ollama.sh` | Stop Ollama server |
| `start-agent.sh` | Start DeepAgents agent |
| `test-agent.sh` | Test connection |
| `project-picker.sh` | Select project from available projects |
| `ollama-agent.sh` | One-shot CLI agent interaction |
| `ollama-agent-terminal.py` | Terminal-separated agent (interactive/one-shot) |
| `setup-cloudflare-skills.sh` | Install Cloudflare skills/MCP wiring |
| `integrate-cloudless.sh` | Integrate with cloudless.gr project |
| `debug-ollama.sh` | Debug Ollama connection |

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview and quick start |
| `PROJECT_WORK_GUIDE.md` | Comprehensive usage guide |
| `docs/ARCHITECTURE.md` | System architecture diagrams |
| `docs/WORKFLOWS.md` | Agent workflow patterns |
| `docs/INTEGRATION_GUIDE.md` | Integration instructions |
| `docs/API_REFERENCE.md` | API documentation |
| `docs/COMPLETE_REFERENCE.md` | Full implementation coverage |
| `docs/CLOUDFLARE_SKILLS.md` | Cloudflare skills/MCP config |
| `docs/OLLAMA_BACKEND.md` | Ollama setup guide |

## 🚀 Entry Points

| Entry Point | Usage |
|-------------|-------|
| `python3 gui.py` | Start terminal GUI |
| `python3 scripts/ollama-agent-terminal.py` | Terminal helper (interactive) |
| `python3 scripts/ollama-agent-terminal.py "prompt"` | Terminal helper (one-shot) |
| `./scripts/ollama-agent.sh "prompt"` | CLI agent via shell script |
| `./scripts/project-picker.sh` | Select project interactively |

## 📦 Exports (from `integrations/__init__.py`)

### Custom Tools
- `create_tool` - Create custom tool
- `Tool` - Tool dataclass
- `ToolRegistry` - Tool registry class
- `ToolResult` - Tool result type
- `AgentToolContext` - Agent tool context
- `get_default_registry` - Get default registry

### Agents
- `create_ollama_agent` - Create basic Ollama agent
- `create_cloudless_agent` - Create cloudless.gr agent
- `TDDAgent` - TDD agent class
- `TerminalAgent` - Terminal agent class
- `SandboxAgent` - Sandbox agent class
- `Orchestrator` - Orchestrator agent class
- `WebAgent` - Web agent class
- `DebugAgent` - Debug agent class
- `AgentStorm` - Agent storm class
- `AgentRole` - Agent role definition

### Cline Integration
- `ClineAdapter` - Cline-compatible adapter
- `NLPProcessor` - NLP command parser
- `ParsedIntent` - Parsed intent data class
- `Intent` - Intent enum

### Cloudless Integration
- `get_cloudflare_skills` - Get available skills
- `get_cloudflare_mcp_servers` - Get MCP servers
- `write_cloudflare_mcp_config` - Write MCP config