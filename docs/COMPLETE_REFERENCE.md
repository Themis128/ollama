# Complete Implementation Reference

This document provides 100% coverage of all implementation details for the DeepAgents + Ollama integration.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Module: deepagents_ollama.py](#module-deepagents_ollamapy)
3. [Module: cloudless_gr_integration.py](#module-cloudless_gr_integrationpy)
4. [Module: tdd_agent.py](#module-tdd_agentpy)
5. [Module: terminal_agent.py](#module-terminal_agentpy)
6. [Module: sandbox_agent.py](#module-sandbox_agentpy)
7. [Module: orchestrator_agent.py](#module-orchestrator_agentpy)
8. [Module: web_agent.py](#module-web_agentpy)
9. [Module: debug_agent.py](#module-debug_agentpy)
10. [Module: agent_storm.py](#module-agent_stormpy)
11. [Scripts Reference](#scripts-reference)

---

## Project Structure

```
/home/tbaltzakis/ollama/
├── .venv/                          # Python virtual environment
├── integrations/
│   ├── __init__.py                 # Package exports
│   ├── deepagents_ollama.py        # Basic Ollama integration
│   ├── cloudless_gr_integration.py # cloudless.gr project integration
│   ├── tdd_agent.py                # Test-Driven Development agent
│   ├── terminal_agent.py           # Terminal execution agent
│   ├── sandbox_agent.py            # Sandboxed execution agent
│   ├── orchestrator_agent.py       # Multi-mode orchestrator
│   ├── web_agent.py                # Internet communication agent
│   ├── debug_agent.py              # Debug and analysis agent
│   └── agent_storm.py              # Parallel multi-agent execution
├── scripts/
│   ├── start-ollama.sh             # Start Ollama server
│   ├── stop-ollama.sh              # Stop Ollama server
│   ├── start-agent.sh              # Start DeepAgents agent
│   ├── test-agent.sh               # Test agent functionality
│   ├── test-project.sh             # Test with project
│   ├── project-picker.sh           # Interactive project picker
│   └── .project_env                # Project environment config
├── docs/
│   ├── ARCHITECTURE.md             # System architecture
│   ├── WORKFLOWS.md                # Workflow documentation
│   ├── INTEGRATION_GUIDE.md        # Integration guide
│   ├── API_REFERENCE.md            # API reference
│   └── COMPLETE_REFERENCE.md       # This file
└── README.md                       # Project overview
```

---

## Module: deepagents_ollama.py

**Location:** `/home/tbaltzakis/ollama/integrations/deepagents_ollama.py`

**Purpose:** Bridge between DeepAgents SDK and Ollama engine for local LLM inference.

### Dependencies

```python
import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from deepagents import create_deep_agent, ProviderProfile, register_provider_profile
from langchain_ollama import ChatOllama
```

### Classes

#### OllamaConfig (dataclass)

Configuration for Ollama DeepAgents integration.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | str | `"http://localhost:11434"` | Ollama server URL |
| `model` | str | `"qwen2.5-coder"` | Model identifier |
| `temperature` | float | `0.1` | Generation temperature |
| `max_tokens` | int | `4096` | Maximum output tokens |
| `top_p` | float | `0.95` | Top-p sampling |
| `streaming` | bool | `True` | Enable streaming |
| `timeout` | int | `120` | Request timeout |
| `api_key` | str | `"dummy"` | API key (not required locally) |

### Functions

#### register_ollama_provider(base_url, api_key, model)

Register Ollama as a DeepAgents provider. Enables `ollama:qwen2.5-coder` style references.

**Side Effects:** Registers provider-wide and model-specific profiles.

#### get_ollama_model(config) -> ChatOllama

Get configured ChatOllama instance.

#### create_ollama_agent(model, base_url, ...) -> Any

Main entry point for creating coding agents.

**Default System Prompt:**
```
You are an expert software developer and coding assistant.
You excel at:
- Writing clean, maintainable code
- Designing robust APIs
- Debugging complex issues
- Writing comprehensive tests
- Following best practices
```

#### async test_ollama_connection(base_url, api_key, model) -> bool

Test Ollama connection and model availability.

#### list_available_models(base_url) -> List[Dict]

List all available models in Ollama.

#### pull_model(model, base_url) -> bool

Pull a model from Ollama registry.

---

## Module: cloudless_gr_integration.py

**Location:** `/home/tbaltzakis/ollama/integrations/cloudless_gr_integration.py`

**Purpose:** DeepAgents integration for the cloudless.gr project.

### Classes

#### CloudlessConfig (dataclass)

| Field | Type | Default |
|-------|------|---------|
| `base_url` | str | `"http://localhost:11434"` |
| `model` | str | `"qwen2.5-coder"` |
| `project_path` | str | `"/home/tbaltzakis/cloudless.gr"` |
| `temperature` | float | `0.1` |
| `max_tokens` | int | `4096` |
| `top_p` | float | `0.95` |
| `streaming` | bool | `True` |
| `timeout` | int | `120` |

### Functions

#### get_cloudless_skills() -> List[str]

Returns skills from `/home/tbaltzakis/cloudless.gr/.deepagents/skills/`.

**Expected Skills:** `code-review`, `database`, `deploy`, `git-workflow`, `monitoring`, `performance`, `security`, `test`

#### create_cloudless_agent(model, base_url, project_path, ...) -> Any

Create DeepAgent with cloudless.gr context.

**Project Context Includes:**
- Framework: Next.js 16 + TypeScript + Tailwind CSS
- Database: DynamoDB (6 tables)
- Auth: AWS Cognito + next-auth v5
- Deployment: AWS Lambda@Edge + K3s failover
- Monitoring: Prometheus + Grafana + Loki + Sentry

#### list_mcp_servers() -> List[str]

List MCP servers from `.deepagents/.mcp.json`.

#### show_project_info()

Display project information to stdout.


---

## Module: tdd_agent.py

**Location:** `/home/tbaltzakis/ollama/integrations/tdd_agent.py`

**Purpose:** Test-Driven Development agent with autonomous self-correction.

### Classes

#### TDDConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | str | `"qwen2.5-coder"` | LLM model name |
| `base_url` | str | `"http://localhost:11434"` | Ollama server URL |
| `project_path` | str | `"/home/tbaltzakis/cloudless.gr"` | Project directory |
| `temperature` | float | `0.1` | Generation temperature |
| `max_iterations` | int | `10` | Max self-correction iterations |
| `timeout` | int | `60` | Per-test timeout in seconds |

#### TDDAgent

**Constructor:** `TDDAgent(config: Optional[TDDConfig] = None)`

**Instance Variables:**
- `config`: TDDConfig instance
- `llm`: ChatOllama instance
- `iteration_count`: Current iteration count
- `history`: List of execution history entries

**Methods:**

##### run_tdd(feature, test_file, implementation_file, test_command) -> Dict

Run complete TDD loop.

**Workflow:**
1. **RED Phase**: Write failing test
2. **GREEN Phase**: Write minimal implementation
3. **SELF-CORRECT**: If tests fail, iterate up to max_iterations

**Returns:**
```python
{
    "status": "success" | "failed",
    "feature": str,
    "test_file": str,
    "implementation_file": str,
    "iterations": int,
    "history": List[Dict],
}
```

**Internal Methods:**

##### _write_failing_test(feature, test_file, implementation_file) -> str

Generate failing test code using LLM.

**LLM Prompt Template:**
```
You are writing a failing test in a TDD cycle.

FEATURE: {feature}
TEST FILE: {test_file}
IMPLEMENTATION FILE: {implementation_file}

Write a comprehensive test file that:
1. Tests all edge cases for the feature
2. Fails initially (before implementation exists)
3. Uses proper TypeScript/JavaScript syntax
4. Includes proper imports and setup
5. Uses Vitest/Jest-style assertions
```

##### _write_implementation(feature, implementation_file, test_file) -> str

Generate minimal implementation code.

##### _self_correct(feature, test_file, implementation_file, test_command) -> Dict

Self-correction loop.

##### _run_test(test_command) -> bool

Execute tests, return True if passing.

##### _write_file(filepath, content)

Write content to file, creating parent directories.

##### _read_file(filepath) -> str

Read content from file.

##### _reset_files(*files)

Reset files to empty state.

---

## Module: terminal_agent.py

**Location:** `/home/tbaltzakis/ollama/integrations/terminal_agent.py`

**Purpose:** Terminal command execution with output parsing.

### Classes

#### TerminalConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `project_path` | str | `"/home/tbaltzakis/cloudless.gr"` | Working directory |
| `sandbox` | bool | `True` | Enable sandbox mode |
| `allowlist` | List[str] | See below | Allowed commands |
| `blocklist` | List[str] | See below | Blocked commands |
| `timeout` | int | `120` | Command timeout |
| `max_retries` | int | `3` | Retry attempts |

**Default Allowlist:**
```python
["npm", "pnpm", "yarn", "node", "python", "uv",
 "git", "ls", "cat", "cd", "pwd", "echo",
 "grep", "sed", "awk", "curl", "wget", "head", 
 "tail", "find", "xxd"]
```

**Default Blocklist:**
```python
["rm -rf", "rm -r", "rm -f",     # Dangerous deletions
 "mkfs", "dd", "fdisk",          # Disk operations
 "chmod 777", "chown",           # Permission changes
 "sudo",                         # Privilege escalation
 "netcat", "nc",                 # Network tools
 "base64 -d"]                    # Encoding tricks
```

#### TerminalAgent

**Constructor:** `TerminalAgent(config: Optional[TerminalConfig] = None)`

**Instance Variables:**
- `config`: TerminalConfig instance
- `execution_history`: List of execution records
- `stdout_history`: List of stdout outputs
- `stderr_history`: List of stderr outputs

**Methods:**

##### execute(command, cwd) -> Dict

Execute shell command with validation.

**Returns:**
```python
{
    "success": bool,
    "exit_code": int,
    "stdout": str,
    "stderr": str,
    "command": str,
    "duration": Optional[float],
}
```

##### parse_output(output, output_type) -> Dict

Parse terminal output.

**Output Types:** `"compiler"`, `"test"`, `"generic"`

**Returns (compiler):**
```python
{
    "has_errors": bool,
    "has_warnings": bool,
    "errors": [{"type": str, "message": str, "location": str}],
    "warnings": [{"type": str, "message": str}],
}
```

**Returns (test):**
```python
{
    "has_errors": bool,
    "failed_tests": [{"name": str, "location": str}],
    "passed_tests": [],
    "summary": {"passed": int, "failed": int, "total": int},
}
```

##### _validate_command(command) -> Dict

Validate against allowlist/blocklist.

##### _parse_compiler_output(output) -> Dict

Parse TypeScript/JavaScript compiler output.

**Patterns:**
- Error: `r'(error|Error):\s*(.+?)\s*\n.*?at\s*(.+?:\d+:\d+)'`
- Warning: `r'(warning|Warning):\s*(.+?)\s*\n'`

##### _parse_test_output(output) -> Dict

Parse Vitest/Jest output.

**Patterns:**
- Pass count: `r'(\d+)\s*pass'`
- Fail count: `r'(\d+)\s*fail'`
- Total count: `r'(\d+)\s*total'`
- Failed test: `r'✕\s*(.+?)\s*\n.*?(?:at\s*)?(.+?:\d+)'`

##### fix_error(error_output, error_type) -> str

Generate fix suggestion.

##### get_history(limit) -> List

Get execution history.

##### clear_history()

Clear all history.


---

## Module: sandbox_agent.py

**Location:** `/home/tbaltzakis/ollama/integrations/sandbox_agent.py`

**Purpose:** Isolated command execution with security controls and audit logging.

### Classes

#### SandboxConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `project_path` | str | `"/home/tbaltzakis/cloudless.gr"` | Working directory |
| `allow_dangerous` | bool | `False` | Allow all commands |
| `enable_isolation` | bool | `True` | Enable environment isolation |
| `max_output_size` | int | `100000` | Max output bytes |
| `timeout` | int | `120` | Command timeout |
| `audit_log_path` | str | `"/tmp/sandbox_audit.log"` | Audit log file |
| `allowlist` | List[str] | See below | Allowed commands |
| `blocklist` | List[str] | See below | Blocked commands |

**Default Allowlist:**
```python
["npm", "pnpm", "yarn", "node", "python", "uv",
 "git", "ls", "cat", "cd", "pwd", "echo",
 "grep", "sed", "awk", "find", "head", "tail",
 "curl", "wget", "xxd", "stat", "file",
 "npx", "tsx", "tsc", "jest", "vitest"]
```

**Default Blocklist:**
```python
["rm -rf", "rm -r", "rm -f",
 "mkfs", "dd", "fdisk", "parted",
 "chmod 777", "chown", "chmod +s",
 "sudo", "su -", "pkexec",
 "netcat", "nc -", "ncat",
 "base64 -d", "xxd -r",
 "exec", "eval", "source",
 "bash -c", "sh -c",
 "wget -e", "curl -d"]
```

#### SandboxAgent

**Constructor:** `SandboxAgent(config: Optional[SandboxConfig] = None)`

**Instance Variables:**
- `config`: SandboxConfig instance
- `audit_log`: List of audit log entries

**Methods:**

##### execute(command, cwd) -> Dict

Execute command in sandbox with full security checks.

**Security Process:**
1. Validate against blocklist
2. Validate against allowlist
3. Setup isolated environment
4. Execute with timeout
5. Truncate output if needed
6. Log to audit log

**Returns:**
```python
{
    "success": bool,
    "exit_code": int,
    "stdout": str,
    "stderr": str,
    "command": str,
    "duration": Optional[float],
}
```

##### execute_safe(command, args) -> Dict

Execute with validated arguments.

**Argument Validation:**
- No dangerous characters: `;`, `|`, `&`, `$`, `` ` ``, `>`, `<`
- No path traversal: `..`

##### get_audit_log() -> List[Dict]

Get all audit log entries.

**Entry Format:**
```python
{
    "timestamp": str,
    "type": "BLOCKED" | "ALLOWLIST_CHECK" | "EXECUTION",
    "command": str,
    "status": "DENIED" | "ALLOWED" | "SUCCESS" | "FAILED",
    "reason": Optional[str],
    "exit_code": Optional[int],
    "stdout_length": Optional[int],
    "stderr_length": Optional[int],
}
```

##### clear_audit_log()

Clear in-memory and file audit log.

##### get_statistics() -> Dict

Get usage statistics.

**Returns:**
```python
{
    "total_executions": int,
    "blocked_commands": int,
    "allowed_commands": int,
    "failed_executions": int,
    "success_rate": float,
}
```

##### export_audit_log(filepath)

Export audit log to JSON file.

**Internal Methods:**

##### _init_audit_log()

Create parent directory for audit log.

##### _add_audit_entry(entry)

Add entry to memory and append to file.

##### _validate_command(command) -> Dict

Validate with logging.

##### _setup_isolation() -> Dict[str, str]

Setup isolated environment.

**Removed Variables:** `LD_PRELOAD`, `LD_LIBRARY_PATH`, `PYTHONPATH`, `HOME`, `USER`, `PATH`

**Set Variables:** `PATH = "/usr/bin:/bin"`, `TMPDIR`

##### _validate_arg(arg) -> bool

Validate single argument.

---

## Module: orchestrator_agent.py

**Location:** `/home/tbaltzakis/ollama/integrations/orchestrator_agent.py`

**Purpose:** Multi-agent orchestration with mode switching.

### Classes

#### AgentMode (Enum)

| Value | Description |
|-------|-------------|
| `ARCHITECT` | System design and planning |
| `CODE` | Implementation and coding |
| `DEBUG` | Error analysis and fixing |
| `ORCHESTRATOR` | Multi-agent coordination |
| `AUTO` | Automatic mode selection |

#### OrchestratorConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | str | `"qwen2.5-coder"` | LLM model |
| `base_url` | str | `"http://localhost:11434"` | Ollama URL |
| `project_path` | str | `"/home/tbaltzakis/cloudless.gr"` | Project path |
| `temperature` | float | `0.1` | Temperature |
| `max_modes` | int | `5` | Max mode switches |

#### Orchestrator

**Constructor:** `Orchestrator(config: Optional[OrchestratorConfig] = None)`

**Instance Variables:**
- `config`: OrchestratorConfig
- `llm`: ChatOllama
- `current_mode`: AgentMode
- `history`: List of execution history
- `mode_prompts`: Dict of mode-specific prompts

**Mode Prompts:**

| Mode | Focus |
|------|-------|
| `architect` | System design, patterns, scalability |
| `code` | Implementation, refactoring, tests |
| `debug` | Error analysis, root causes, fixes |
| `orchestrator` | Mode switching, task decomposition |
| `auto` | Automatic mode selection |

**Methods:**

##### execute(task, mode, context) -> Dict

Execute task using specified mode.

**Returns (single mode):**
```python
{
    "success": bool,
    "mode": str,
    "task": str,
    "output": str,
    "mode_switches": int,
    "history": List[Dict],
}
```

**Returns (auto mode):**
```python
{
    "success": bool,
    "task": str,
    "stages": [{"mode": str, "output": str}],
    "final_output": str,
    "total_stages": int,
}
```

##### switch_mode(new_mode) -> bool

Switch to new agent mode.

##### get_mode_history() -> List[str]

Get modes used in session.

##### _auto_mode_execute(task, context) -> Dict

Execute with automatic mode switching.

**Auto Workflow:**
1. Architect: Create plan
2. Code: Implement plan
3. Debug: Verify and fix

##### _execute_with_mode(mode, prompt, context) -> str

Execute prompt with specific mode.


---

## Module: web_agent.py

**Location:** `/home/tbaltzakis/ollama/integrations/web_agent.py`

**Purpose:** Internet communication with safety controls.

### Classes

#### WebConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `rate_limit` | int | `10` | Requests per minute |
| `timeout` | int | `30` | Request timeout |
| `max_retries` | int | `3` | Retry attempts |
| `cache_dir` | str | `"/tmp/web_agent_cache"` | Cache directory |
| `safe_domains` | List[str] | See below | Allowed domains |

**Default Safe Domains:**
```python
["docs.langchain.com", "nextjs.org", "react.dev",
 "typescriptlang.org", "stripe.com", "aws.amazon.com",
 "github.com", "stackoverflow.com", "w3.org", "wikipedia.org"]
```

#### WebAgent

**Constructor:** `WebAgent(config: Optional[WebConfig] = None)`

**Instance Variables:**
- `config`: WebConfig
- `session`: requests.Session with retry policy
- `request_count`: Number of requests made
- `last_request_time`: Timestamp of last request

**Methods:**

##### search(query, max_results) -> List[Dict]

Search using DuckDuckGo Instant Answer API.

**Returns:**
```python
[{"title": str, "url": str, "snippet": str, "source": "duckduckgo"}]
```

##### fetch(url, max_length) -> Dict

Fetch content from URL.

**Process:**
1. Check cache
2. Validate URL domain
3. Enforce rate limit
4. Fetch with timeout
5. Cache result

**Returns:**
```python
{
    "success": bool,
    "url": str,
    "content": str,
    "cached": bool,
    "status_code": Optional[int],
}
```

##### fetch_selective(url, search_phrase) -> Dict

Fetch content matching search phrase.

**Returns:**
```python
{
    "success": bool,
    "url": str,
    "content": str,  # Context around match
    "matched": bool,
    "search_phrase": str,
}
```

##### research(topic, sources) -> Dict

Research topic using multiple sources.

**Returns:**
```python
{
    "topic": str,
    "sources_used": [{"title": str, "url": str, "source": str}],
    "summaries": [{"source": str, "summary": str, "url": str}],
    "key_findings": List[str],
}
```

##### get_api_docs(api_name) -> Dict

Fetch API documentation.

**Supported APIs:** `stripe`, `nextjs`, `aws`, `langchain`, `react`, `typescript`

##### check_url_exists(url) -> bool

Check if URL exists using HEAD request.

##### get_last_request_count() -> int

Get request count.

**Internal Methods:**

##### _setup_cache()

Create cache directory.

##### _setup_session()

Setup requests session with retry policy.

##### _check_rate_limit()

Enforce rate limiting with sleep.

##### _is_safe_url(url) -> bool

Check if URL is from safe domain.

##### _get_cache_key(url) -> str

Generate SHA256 cache key.

##### _get_cached(url) -> Optional[str]

Get cached content.

##### _cache(url, content)

Cache content.

##### _fallback_search(query, max_results) -> List[Dict]

Fallback search using remote_web_search.

---

## Module: debug_agent.py

**Location:** `/home/tbaltzakis/ollama/integrations/debug_agent.py`

**Purpose:** Log analysis and self-fixing capabilities.

### Classes

#### DebugConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | str | `"qwen2.5-coder"` | LLM model |
| `base_url` | str | `"http://localhost:11434"` | Ollama URL |
| `project_path` | str | `"/home/tbaltzakis/cloudless.gr"` | Project path |
| `temperature` | float | `0.1` | Temperature |
| `max_analysis_lines` | int | `1000` | Max lines to analyze |

#### DebugAgent

**Constructor:** `DebugAgent(config: Optional[DebugConfig] = None)`

**Instance Variables:**
- `config`: DebugConfig
- `analysis_history`: List of analysis results

**Methods:**

##### analyze_error(error_output, file_path) -> Dict

Analyze error and provide diagnosis.

**Returns:**
```python
{
    "timestamp": str,
    "error_type": str,  # "type_error", "syntax_error", etc.
    "root_cause": str,
    "location": {"file": str, "line": int, "function": str},
    "suggested_fix": str,
    "related_files": List[str],
    "severity": str,  # "critical", "high", "medium", "low"
}
```

**Error Types:**
- `type_error`: TypeError indicators
- `syntax_error`: SyntaxError indicators
- `import_error`: ImportError indicators
- `attribute_error`: AttributeError indicators
- `key_error`: KeyError indicators
- `index_error`: IndexError indicators
- `test_failure`: Test fail indicators
- `compilation_error`: Build/compile errors
- `runtime_error`: Default fallback

##### analyze_logs(log_file, max_lines) -> Dict

Analyze log file for issues.

**Returns:**
```python
{
    "file": str,
    "timestamp": str,
    "total_lines": int,
    "issues_found": [{"type": str, "line": str}],
    "patterns_detected": [{"pattern": str, "count": int, "examples": List[str]}],
    "summary": str,
}
```

**Pattern Detection:**
- `errors`: `error|ERROR|Error`
- `warnings`: `warning|WARNING|Warning|warn`
- `exceptions`: `exception|Exception|EXCEPTION`
- `stacktraces`: `at\s+\w+|Traceback|Stack trace`
- `timeouts`: `timeout|timed out|deadline exceeded`
- `connection`: `connection|network|socket`
- `memory`: `memory|oom|heap`

##### generate_fix(error_output, file_path, implementation) -> str

Generate fix for error.

##### self_fix(error_output, file_path, test_command) -> Dict

Attempt to self-fix error.

**Returns:**
```python
{
    "success": bool,
    "error": str,
    "file": str,
    "fix_generated": Optional[str],
    "fix_applied": bool,
    "test_passed": bool,
}
```

##### get_analysis_history() -> List[Dict]

Get analysis history.

**Internal Methods:**

##### _classify_error(error_output) -> str

Classify error type from output.

##### _identify_root_cause(error_output, file_path) -> str

Identify root cause using LLM.

##### _extract_location(error_output, file_path) -> Dict

Extract file, line, function from error.

**Patterns:**
- Line: `r"line\s+(\d+)"`, `r":(\d+):"`, `r"at\s+\w+\s+\(.*:(\d+)\)"`
- Function: `r"in\s+(\w+)\s*\("`, `r"function\s+(\w+)"`, `r"at\s+(\w+)"`

##### _suggest_fix(error_output) -> str

Suggest fix using LLM.

##### _identify_related_files(error_output) -> List[str]

Extract related files from error.

##### _assess_severity(error_output) -> str

Assess error severity.

##### _invoke_llm(prompt) -> str

Invoke LLM with prompt.


---

## Module: agent_storm.py

**Location:** `/home/tbaltzakis/ollama/integrations/agent_storm.py`

**Purpose:** Parallel multi-agent execution pattern.

### Classes

#### AgentStormConfig (dataclass)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model` | str | `"qwen2.5-coder"` | LLM model |
| `base_url` | str | `"http://localhost:11434"` | Ollama URL |
| `project_path` | str | `"/home/tbaltzakis/cloudless.gr"` | Project path |
| `temperature` | float | `0.1` | Temperature |
| `num_agents` | int | `4` | Number of agents |
| `max_workers` | int | `4` | ThreadPool workers |
| `synthesizer_model` | str | `"qwen2.5-coder"` | Synthesizer model |
| `timeout` | int | `300` | Total timeout |

#### AgentRole (dataclass)

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Role name |
| `system_prompt` | str | System prompt for role |
| `focus` | str | Focus area description |

**Default Roles:**

| Role | Focus |
|------|-------|
| `architect` | System design, patterns, scalability |
| `backend` | API, database, business logic |
| `security` | Vulnerabilities, auth, compliance |
| `testing` | Coverage, edge cases, automation |
| `frontend` | UI, UX, accessibility |
| `devops` | Infrastructure, deployment, CI/CD |

#### AgentStorm

**Constructor:** `AgentStorm(config: Optional[AgentStormConfig] = None)`

**Instance Variables:**
- `config`: AgentStormConfig
- `roles`: List of AgentRole (DEFAULT_ROLES)
- `results`: List of storm results

**Methods:**

##### storm(task, prompt, num_agents, custom_roles) -> Dict

Run Agent Storm with parallel agents.

**Returns:**
```python
{
    "success": bool,
    "task": str,
    "num_agents": int,
    "duration_seconds": float,
    "individual_results": [{"role": str, "success": bool, "output": str}],
    "synthesis": {"timestamp": str, "synthesis": str, "input_count": int},
}
```

##### storm_with_roles(task, prompt, roles) -> Dict

Run with specific role names.

**Parameters:**
- `roles`: List of role names like `["architect", "backend", "security"]`

##### parallel_tasks(task, subtasks) -> Dict

Execute subtasks in parallel.

**Returns:**
```python
{
    "success": bool,
    "task": str,
    "num_subtasks": int,
    "duration_seconds": float,
    "results": [{"subtask": str, "role": str, "success": bool, "output": str}],
}
```

##### get_results() -> List[Dict]

Get all storm results.

##### clear_results()

Clear stored results.

**Internal Methods:**

##### _execute_parallel(prompts) -> List[Dict]

Execute agents in parallel using ThreadPoolExecutor.

##### _execute_agent(role, prompt) -> Dict

Execute single agent.

##### _synthesize_results(task, results) -> Dict

Synthesize results using synthesizer agent.

---

## Scripts Reference

### start-ollama.sh

**Purpose:** Start Ollama server and display available models.

**Process:**
1. Check if Ollama is already running (curl localhost:11434)
2. If not running, try systemctl start ollama
3. If systemctl fails, run `ollama serve` in background
4. Wait 5 seconds for startup
5. Display available models

**Usage:**
```bash
./scripts/start-ollama.sh
```

### stop-ollama.sh

**Purpose:** Stop Ollama server.

**Process:**
1. Run `sudo systemctl stop ollama`
2. Verify server is stopped

**Usage:**
```bash
./scripts/stop-ollama.sh
```

### start-agent.sh

**Purpose:** Start DeepAgents + Ollama agent.

**Process:**
1. Navigate to project root
2. Activate virtual environment
3. Run `python3 integrations/deepagents_ollama.py`

**Usage:**
```bash
./scripts/start-agent.sh
```

### test-agent.sh

**Purpose:** Test DeepAgents + Ollama integration.

**Process:**
1. Navigate to project root
2. Activate virtual environment
3. Run Python test code that:
   - Creates agent with `create_ollama_agent()`
   - Sends test query about Fibonacci
   - Prints output

**Usage:**
```bash
./scripts/test-agent.sh
```

### test-project.sh

**Purpose:** Test agent with selected project.

**Process:**
1. Source project environment from `.project_env`
2. Check for DeepAgents setup files
3. Verify `dcode` CLI is available
4. Display usage examples
5. List available skills

**Usage:**
```bash
./scripts/test-project.sh
```

### project-picker.sh

**Purpose:** Interactive project picker UI.

**Available Projects:**
- cloudless.gr: `/home/tbaltzakis/cloudless.gr`
- DeepAgents SDK: `/home/tbaltzakis/Deep agents/deepagents`
- vLLM: `/home/tbaltzakis/vLLM`

**Process:**
1. Display menu with numbered options
2. Read user selection
3. Validate input
4. Create `.project_env` file with:
   - `PROJECT_NAME`
   - `PROJECT_PATH`
   - `DEEP_AGENTS_PROJECT_ROOT`

**Usage:**
```bash
./scripts/project-picker.sh
```

**Output Example:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DeepAgents + Ollama - Project Picker
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Available Projects:

  1. cloudless.gr
     Path: /home/tbaltzakis/cloudless.gr

  2. DeepAgents SDK
     Path: /home/tbaltzakis/Deep agents/deepagents

  3. vLLM
     Path: /home/tbaltzakis/vLLM

  4. Cancel

Select a project (1-4):
```

---

## Complete Type Reference

### Import Exports

**From `integrations/__init__.py`:**

```python
from integrations import (
    create_ollama_agent,      # Requires deepagents package
    create_cloudless_agent,   # Requires deepagents package
    TDDAgent,                 # Available
    TerminalAgent,            # Available
    SandboxAgent,             # Available
    Orchestrator,             # Available
    WebAgent,                 # Available
    DebugAgent,               # Available
    AgentStorm,               # Available
    AgentRole,                # Available
)
```

### Configuration Classes

```python
from integrations.deepagents_ollama import OllamaConfig
from integrations.cloudless_gr_integration import CloudlessConfig
from integrations.tdd_agent import TDDConfig
from integrations.terminal_agent import TerminalConfig
from integrations.sandbox_agent import SandboxConfig
from integrations.orchestrator_agent import OrchestratorConfig, AgentMode
from integrations.web_agent import WebConfig
from integrations.debug_agent import DebugConfig
from integrations.agent_storm import AgentStormConfig, AgentRole
```

### Return Type Summary

| Method | Success Key | Error Key |
|--------|-------------|-----------|
| `TDDAgent.run_tdd()` | `status: "success"` | `status: "failed"` |
| `TerminalAgent.execute()` | `success: True` | `success: False` |
| `SandboxAgent.execute()` | `success: True` | `success: False` |
| `Orchestrator.execute()` | `success: True` | `success: False` |
| `WebAgent.fetch()` | `success: True` | `success: False` |
| `DebugAgent.analyze_error()` | Always returns diagnosis | N/A |
| `AgentStorm.storm()` | `success: True` | `success: False` |
