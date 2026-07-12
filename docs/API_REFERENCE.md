# API Reference

Complete API documentation for all modules in the DeepAgents + Ollama integration.

## Table of Contents

1. [DeepAgents + Ollama Base](#deepagents--ollama-base)
2. [ClineAdapter](#clineadapter)
3. [NLPProcessor](#nlpprocessor)
4. [TDDAgent](#tddagent)
5. [TerminalAgent](#terminalagent)
6. [SandboxAgent](#sandboxagent)
7. [Orchestrator](#orchestrator)
8. [WebAgent](#webagent)
9. [DebugAgent](#debugagent)
10. [AgentStorm](#agentstorm)
11. [Custom Tools](#custom-tools)
12. [Error Handling](#error-handling)

---

## DeepAgents + Ollama Base

Base integration module providing the foundation for all Ollama-powered agents.

### Module

```python
from integrations.deepagents_ollama import (
    create_ollama_agent,
    create_ollama_agent_with_tools,
    OllamaConfig,
    register_ollama_provider,
    get_ollama_model,
    list_available_models,
    pull_model,
)
```

### Configuration

```python
@dataclass
class OllamaConfig:
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder"
    temperature: float = 0.1  # Lower for coding tasks
    max_tokens: int = 4096
    top_p: float = 0.95
    streaming: bool = True
    timeout: int = 120
    api_key: str = "dummy"  # Not required for local Ollama
```

### Functions

#### create_ollama_agent

Create a DeepAgent powered by Ollama.

```python
def create_ollama_agent(
    model: str = "qwen2.5-coder",
    base_url: str = "http://localhost:11434",
    api_key: str = "dummy",
    system_prompt: Optional[str] = None,
    tools: Optional[List[Any]] = None,
    middleware: Optional[List[Any]] = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    timeout: int = 120,
) -> Any
```

**Parameters:**
- `model` (str): Ollama model name (qwen2.5-coder, llama3.1, mistral, etc.)
- `base_url` (str): Ollama server URL
- `api_key` (str): API key (dummy for local Ollama)
- `system_prompt` (Optional[str]): Custom system prompt
- `tools` (Optional[List[Any]]): Optional list of custom tools
- `middleware` (Optional[List[Any]]): Optional middleware list
- `temperature` (float): Generation temperature (lower = more precise)
- `max_tokens` (int): Maximum output tokens
- `timeout` (int): Request timeout in seconds

**Returns:**
- `Any`: Configured DeepAgent instance

**Example:**
```python
from integrations import create_ollama_agent

agent = create_ollama_agent(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    system_prompt="You are an expert Python developer...",
)

result = agent.invoke({"messages": "Create a REST API with FastAPI"})
```

#### register_ollama_provider

Register Ollama as a DeepAgents provider.

```python
def register_ollama_provider(
    base_url: str = "http://localhost:11434",
    api_key: str = "dummy",
    model: str = "qwen2.5-coder",
) -> None
```

**Parameters:**
- `base_url` (str): Ollama server URL
- `api_key` (str): API key (dummy works for local Ollama)
- `model` (str): Model identifier

**Example:**
```python
from integrations.deepagents_ollama import register_ollama_provider

register_ollama_provider(
    base_url="http://localhost:11434",
    model="qwen2.5-coder",
)
# Now you can use: ollama:qwen2.5-coder as model string
```

#### list_available_models

List all available models in Ollama.

```python
def list_available_models(base_url: str = "http://localhost:11434") -> List[Dict[str, Any]]
```

**Returns:**
```python
[
    {"name": "qwen2.5-coder:latest", "size": 123456789, ...},
    {"name": "llama3.1:latest", "size": 987654321, ...},
    ...
]
```

#### pull_model

Pull a model from Ollama registry.

```python
def pull_model(model: str = "qwen2.5-coder", base_url: str = "http://localhost:11434") -> bool
```

**Returns:**
- `bool`: True if successful

---

## ClineAdapter

Cline-compatible tool interface for DeepAgents + Ollama integration.

### Module

```python
from integrations.cline_adapter import ClineAdapter
```

### Constructor

```python
ClineAdapter(project_path: Optional[str] = None)
```

**Parameters:**
- `project_path` (Optional[str]): Project path for context (uses PROJECT_PATH env or cwd)

### Default Tools

The ClineAdapter provides 11 tools by default:

| Tool | Description |
|------|-------------|
| `list_files` | List files in a directory with max_depth filter |
| `read_file` | Read file content by path |
| `write_file` | Write content to a file |
| `run_command` | Execute terminal commands |
| `ask_agent` | Query Ollama LLM |
| `list_models` | List available Ollama models |
| `pull_model` | Download a new model |
| `check_ollama` | Check server status |
| `search_files` | Search for files matching a pattern |
| `get_file_info` | Get detailed file information |
| `analyze_code` | Analyze code structure and quality |
| `generate_test` | Generate test scaffolding for a file |

### Methods

#### run_tool

Execute a tool and return Cline-compatible response.

```python
def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]
```

**Parameters:**
- `tool_name` (str): Name of the tool to execute
- `params` (Dict[str, Any]): Parameters for the tool

**Returns:**
```python
# Success response
{
    "success": True,
    # ... tool-specific fields
}

# Error response
{
    "success": False,
    "error": str,
    "available_tools": List[str],  # Only on unknown tool error
}
```

**Example:**
```python
from integrations import ClineAdapter

adapter = ClineAdapter(project_path="/home/tbaltzakis/my-project")

# List files
result = adapter.run_tool("list_files", {"max_depth": 2})

# Read a file
result = adapter.run_tool("read_file", {"path": "src/app.py"})

# Write a file
result = adapter.run_tool("write_file", {
    "path": "src/output.py",
    "content": "print('Hello, World!')"
})

# Run a command
result = adapter.run_tool("run_command", {
    "command": "ls -la",
    "cwd": "/home/tbaltzakis/my-project"
})
```

---

## NLPProcessor

Natural language command parsing with confidence scoring.

### Module

```python
from integrations.nlp_processor import NLPProcessor, ParsedIntent, Intent
```

### Enum

```python
class Intent(Enum):
    ANALYZE = "analyze"
    CODE = "code"
    TEST = "test"
    RESEARCH = "research"
    OLLAMA = "ollama"
    PROJECT = "project"
    UNKNOWN = "unknown"
```

### Dataclass

```python
@dataclass
class ParsedIntent:
    intent: Intent
    action: str
    confidence: float
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    requires_confirmation: bool = False
```

### Constructor

```python
NLPProcessor()
```

### Methods

#### parse

Parse natural language command into structured intent.

```python
def parse(self, command: str, project_context: Optional[str] = None) -> ParsedIntent
```

**Parameters:**
- `command` (str): Natural language command
- `project_context` (Optional[str]): Project path for context

**Returns:**
- `ParsedIntent`: Structured intent with confidence scores

**Example:**
```python
from integrations import NLPProcessor

nlp = NLPProcessor()

intent = nlp.parse("analyze codebase for issues")

print(f"Intent: {intent.intent}")
print(f"Action: {intent.action}")
print(f"Confidence: {intent.confidence}")
print(f"Parameters: {intent.parameters}")
```

---

## Custom Tools

Tool registry framework for creating and managing custom agent tools.

### Module

```python
from integrations.custom_tools import (
    create_tool,
    Tool,
    ToolRegistry,
    ToolResult,
    AgentToolContext,
    get_default_registry,
)
```

### Functions

#### create_tool

Create a custom tool function.

```python
def create_tool(
    func: Callable,
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
) -> Tool
```

**Example:**
```python
from integrations import create_tool

def my_custom_tool(input: str) -> str:
    """Process input and return result."""
    return f"Processed: {input}"

tool = create_tool(
    my_custom_tool,
    name="process_text",
    description="Process text with custom logic",
)
```

#### get_default_registry

Get the default tool registry.

```python
def get_default_registry() -> ToolRegistry
```

### Classes

#### Tool

Represents a tool with metadata.

```python
@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]
```

#### ToolRegistry

Registry for managing tools.

```python
class ToolRegistry:
    def register(self, tool: Tool) -> None
    def unregister(self, name: str) -> None
    def get(self, name: str) -> Optional[Tool]
    def list_tools(self) -> List[str]
    def execute(self, name: str, **kwargs) -> ToolResult
```

#### ToolResult

Result of tool execution.

```python
@dataclass
class ToolResult:
    success: bool
    result: Any = None
    error: Optional[str] = None
```

---

## TDDAgent

Test-Driven Development agent with autonomous self-correction.

### Module

```python
from integrations.tdd_agent import TDDAgent, TDDConfig
```

### Configuration

```python
@dataclass
class TDDConfig:
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    max_iterations: int = 10
    timeout: int = 60
```

### Constructor

```python
TDDAgent(config: Optional[TDDConfig] = None)
```

**Parameters:**
- `config` (Optional[TDDConfig]): Configuration object. Uses defaults if not provided.

**Example:**
```python
# Default configuration
agent = TDDAgent()

# Custom configuration
config = TDDConfig(
    model="qwen2.5-coder",
    project_path="/path/to/project",
    max_iterations=15,
)
agent = TDDAgent(config)
```

### Methods

#### run_tdd

Run complete TDD loop for a feature.

```python
def run_tdd(
    self,
    feature: str,
    test_file: str,
    implementation_file: str,
    test_command: str = "pnpm test",
) -> Dict[str, Any]
```

**Parameters:**
- `feature` (str): Description of the feature to implement
- `test_file` (str): Path to test file
- `implementation_file` (str): Path to implementation file
- `test_command` (str): Command to run tests (default: "pnpm test")

**Returns:**
```python
{
    "status": "success" | "failed",
    "feature": str,
    "test_file": str,
    "implementation_file": str,
    "iterations": int,
    "history": List[Dict[str, Any]],
}
```

**Example:**
```python
result = agent.run_tdd(
    feature="Create user authentication API endpoint",
    test_file="src/api/auth/route.test.ts",
    implementation_file="src/api/auth/route.ts",
    test_command="pnpm test",
)

if result["status"] == "success":
    print(f"Completed in {result['iterations']} iterations")
```

---

## TerminalAgent

Terminal command execution with output parsing.

### Module

```python
from integrations.terminal_agent import TerminalAgent, TerminalConfig
```

### Configuration

```python
@dataclass
class TerminalConfig:
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    sandbox: bool = True
    allowlist: List[str] = field(default_factory=lambda: [...])
    blocklist: List[str] = field(default_factory=lambda: [...])
    timeout: int = 120
    max_retries: int = 3
```

### Constructor

```python
TerminalAgent(config: Optional[TerminalConfig] = None)
```

### Methods

#### execute

Execute a shell command.

```python
def execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]
```

**Parameters:**
- `command` (str): Shell command to execute
- `cwd` (Optional[str]): Working directory (defaults to project path)

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

**Example:**
```python
agent = TerminalAgent()
result = agent.execute("pnpm test")

if result['success']:
    print(result['stdout'])
else:
    print(f"Error: {result['stderr']}")
```

#### parse_output

Parse terminal output to extract structured information.

```python
def parse_output(self, output: str, output_type: str = "generic") -> Dict[str, Any]
```

**Parameters:**
- `output` (str): Raw output from command
- `output_type` (str): Type of output ("compiler", "test", "generic")

**Returns:**
```python
# For compiler output
{
    "has_errors": bool,
    "has_warnings": bool,
    "errors": List[Dict[str, str]],
    "warnings": List[Dict[str, str]],
}

# For test output
{
    "has_errors": bool,
    "failed_tests": List[Dict[str, str]],
    "passed_tests": List[Dict[str, str]],
    "summary": Dict[str, int],
}
```

**Example:**
```python
result = agent.execute("pnpm test")
parsed = agent.parse_output(result['stdout'], output_type="test")

print(f"Passed: {parsed['summary'].get('passed', 0)}")
print(f"Failed: {parsed['summary'].get('failed', 0)}")

for test in parsed['failed_tests']:
    print(f"Failed: {test['name']} at {test['location']}")
```

#### fix_error

Generate fix for error output.

```python
def fix_error(self, error_output: str, error_type: str = "generic") -> str
```

**Parameters:**
- `error_output` (str): Raw error output
- `error_type` (str): Type of error ("compiler", "test", "generic")

**Returns:**
- `str`: Suggested fix code

#### get_history

Get execution history.

```python
def get_history(self, limit: int = 10) -> List[Dict[str, Any]]
```

#### clear_history

Clear execution history.

```python
def clear_history(self) -> None
```

---

## SandboxAgent

Isolated execution with security controls.

### Module

```python
from integrations.sandbox_agent import SandboxAgent, SandboxConfig
```

### Configuration

```python
@dataclass
class SandboxConfig:
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    allow_dangerous: bool = False
    enable_isolation: bool = True
    max_output_size: int = 100000
    timeout: int = 120
    audit_log_path: str = "/tmp/sandbox_audit.log"
    allowlist: List[str] = field(default_factory=lambda: [...])
    blocklist: List[str] = field(default_factory=lambda: [...])
```

### Constructor

```python
SandboxAgent(config: Optional[SandboxConfig] = None)
```

### Methods

#### execute

Execute command in sandbox.

```python
def execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]
```

**Parameters:**
- `command` (str): Command to execute
- `cwd` (Optional[str]): Working directory

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

**Example:**
```python
sandbox = SandboxAgent()

# Execute safe command
result = sandbox.execute("pnpm build")
print(f"Build: {'SUCCESS' if result['success'] else 'FAILED'}")

# Try dangerous command (will be blocked)
result = sandbox.execute("rm -rf /")
print(result['error'])  # "Command not allowed: Blocked: 'rm -rf'"
```

#### execute_safe

Execute command with safe arguments only.

```python
def execute_safe(self, command: str, args: List[str]) -> Dict[str, Any]
```

**Parameters:**
- `command` (str): Base command
- `args` (List[str]): List of safe arguments

**Example:**
```python
result = sandbox.execute_safe("git", ["checkout", "main"])
```

#### get_audit_log

Get audit log entries.

```python
def get_audit_log(self) -> List[Dict[str, Any]]
```

**Returns:**
```python
[
    {
        "timestamp": str,
        "type": "BLOCKED" | "ALLOWLIST_CHECK" | "EXECUTION",
        "command": str,
        "status": "DENIED" | "ALLOWED" | "SUCCESS" | "FAILED",
        "reason": Optional[str],
        "exit_code": Optional[int],
    },
    ...
]
```

#### clear_audit_log

Clear audit log.

```python
def clear_audit_log(self) -> None
```

#### get_statistics

Get sandbox usage statistics.

```python
def get_statistics(self) -> Dict[str, Any]
```

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

#### export_audit_log

Export audit log to file.

```python
def export_audit_log(self, filepath: str) -> None
```

---

## Orchestrator

Multi-agent orchestration with mode switching.

### Module

```python
from integrations.orchestrator_agent import Orchestrator, OrchestratorConfig, AgentMode
```

### Configuration

```python
@dataclass
class OrchestratorConfig:
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    max_modes: int = 5
```

### Enum

```python
class AgentMode(Enum):
    ARCHITECT = "architect"
    CODE = "code"
    DEBUG = "debug"
    ORCHESTRATOR = "orchestrator"
    AUTO = "auto"
```

### Constructor

```python
Orchestrator(config: Optional[OrchestratorConfig] = None)
```

### Methods

#### execute

Execute task using appropriate mode(s).

```python
def execute(
    self,
    task: str,
    mode: str = "auto",
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]
```

**Parameters:**
- `task` (str): Task description
- `mode` (str): Agent mode ("auto", "architect", "code", "debug", "orchestrator")
- `context` (Optional[Dict[str, Any]]): Additional context for the task

**Returns:**
```python
# For single mode
{
    "success": bool,
    "mode": str,
    "task": str,
    "output": str,
    "mode_switches": int,
    "history": List[Dict[str, Any]],
}

# For auto mode
{
    "success": bool,
    "task": str,
    "stages": List[Dict[str, str]],
    "final_output": str,
    "total_stages": int,
}
```

**Example:**
```python
orchestrator = Orchestrator()

# Single mode
result = orchestrator.execute(
    task="Design the authentication system",
    mode="architect",
)
print(result['output'])

# Auto mode (planning -> implementation -> verification)
result = orchestrator.execute(
    task="Implement user registration with email verification",
    mode="auto",
)
print(result['final_output'])
```

#### switch_mode

Switch to a new agent mode.

```python
def switch_mode(self, new_mode: str) -> bool
```

**Parameters:**
- `new_mode` (str): New mode name

**Returns:**
- `bool`: True if switch successful

#### get_mode_history

Get list of modes used in current session.

```python
def get_mode_history(self) -> List[str]
```

---

## WebAgent

Internet communication with safety controls.

### Module

```python
from integrations.web_agent import WebAgent, WebConfig
```

### Configuration

```python
@dataclass
class WebConfig:
    rate_limit: int = 10
    timeout: int = 30
    max_retries: int = 3
    cache_dir: str = "/tmp/web_agent_cache"
    safe_domains: List[str] = field(default_factory=lambda: [...])
```

### Constructor

```python
WebAgent(config: Optional[WebConfig] = None)
```

### Methods

#### search

Search the web for information.

```python
def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]
```

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum number of results

**Returns:**
```python
[
    {
        "title": str,
        "url": str,
        "snippet": str,
        "source": str,
    },
    ...
]
```

**Example:**
```python
web = WebAgent()
results = web.search("Next.js API route patterns", max_results=5)

for result in results:
    print(f"{result['title']}: {result['url']}")
```

#### fetch

Fetch content from a URL.

```python
def fetch(self, url: str, max_length: int = 50000) -> Dict[str, Any]
```

**Parameters:**
- `url` (str): URL to fetch
- `max_length` (int): Maximum content length to return

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

**Example:**
```python
result = web.fetch("https://nextjs.org/docs")

if result['success']:
    print(result['content'][:1000])
```

#### fetch_selective

Fetch specific content matching a search phrase.

```python
def fetch_selective(self, url: str, search_phrase: str) -> Dict[str, Any]
```

**Parameters:**
- `url` (str): URL to fetch
- `search_phrase` (str): Phrase to search for in content

**Returns:**
```python
{
    "success": bool,
    "url": str,
    "content": str,
    "matched": bool,
    "search_phrase": str,
}
```

#### research

Research a topic using multiple sources.

```python
def research(self, topic: str, sources: int = 3) -> Dict[str, Any]
```

**Parameters:**
- `topic` (str): Topic to research
- `sources` (int): Number of sources to use

**Returns:**
```python
{
    "topic": str,
    "sources_used": List[Dict[str, str]],
    "summaries": List[Dict[str, str]],
    "key_findings": List[str],
}
```

**Example:**
```python
research = web.research("DynamoDB best practices", sources=3)

print(f"Topic: {research['topic']}")
print(f"Sources: {len(research['sources_used'])}")

for finding in research['key_findings']:
    print(f"- {finding}")
```

#### get_api_docs

Fetch API documentation.

```python
def get_api_docs(self, api_name: str) -> Dict[str, Any]
```

**Parameters:**
- `api_name` (str): Name of the API (e.g., "Stripe", "Next.js", "AWS")

**Example:**
```python
docs = web.get_api_docs("stripe")
if docs['success']:
    print(docs['content'][:1000])
```

#### check_url_exists

Check if URL exists (HEAD request).

```python
def check_url_exists(self, url: str) -> bool
```

#### get_last_request_count

Get the number of requests made in current session.

```python
def get_last_request_count(self) -> int
```

---

## DebugAgent

Log analysis and self-fixing capabilities.

### Module

```python
from integrations.debug_agent import DebugAgent, DebugConfig
```

### Configuration

```python
@dataclass
class DebugConfig:
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    max_analysis_lines: int = 1000
```

### Constructor

```python
DebugAgent(config: Optional[DebugConfig] = None)
```

### Methods

#### analyze_error

Analyze error output and provide diagnosis.

```python
def analyze_error(
    self,
    error_output: str,
    file_path: Optional[str] = None,
) -> Dict[str, Any]
```

**Parameters:**
- `error_output` (str): Raw error output
- `file_path` (Optional[str]): Path to file where error occurred

**Returns:**
```python
{
    "timestamp": str,
    "error_type": str,  # "type_error", "syntax_error", etc.
    "root_cause": str,
    "location": {
        "file": str,
        "line": Optional[int],
        "function": Optional[str],
    },
    "suggested_fix": str,
    "related_files": List[str],
    "severity": str,  # "critical", "high", "medium", "low"
}
```

**Example:**
```python
debugger = DebugAgent()

error = """
TypeError: Cannot read properties of undefined (reading 'id')
    at UserController.getUser (src/controllers/user.ts:25:15)
"""

diagnosis = debugger.analyze_error(error, "src/controllers/user.ts")

print(f"Error Type: {diagnosis['error_type']}")
print(f"Root Cause: {diagnosis['root_cause']}")
print(f"Severity: {diagnosis['severity']}")
print(f"Suggested Fix: {diagnosis['suggested_fix']}")
```

#### analyze_logs

Analyze log file for issues.

```python
def analyze_logs(
    self,
    log_file: str,
    max_lines: int = 1000,
) -> Dict[str, Any]
```

**Parameters:**
- `log_file` (str): Path to log file
- `max_lines` (int): Maximum lines to analyze

**Returns:**
```python
{
    "file": str,
    "timestamp": str,
    "total_lines": int,
    "issues_found": List[Dict[str, str]],
    "patterns_detected": List[Dict[str, Any]],
    "summary": str,
}
```

**Example:**
```python
analysis = debugger.analyze_logs("/var/log/app.log")

print(f"Summary: {analysis['summary']}")

for pattern in analysis['patterns_detected']:
    print(f"{pattern['pattern']}: {pattern['count']} occurrences")
```

#### generate_fix

Generate fix for error.

```python
def generate_fix(
    self,
    error_output: str,
    file_path: str,
    implementation: Optional[str] = None,
) -> str
```

**Parameters:**
- `error_output` (str): Error output
- `file_path` (str): Path to file to fix
- `implementation` (Optional[str]): Current implementation code

**Returns:**
- `str`: Fixed code

#### self_fix

Attempt to self-fix an error.

```python
def self_fix(
    self,
    error_output: str,
    file_path: str,
    test_command: str = "pnpm test",
) -> Dict[str, Any]
```

**Parameters:**
- `error_output` (str): Error output
- `file_path` (str): Path to file to fix
- `test_command` (str): Command to run tests

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

#### get_analysis_history

Get analysis history.

```python
def get_analysis_history(self) -> List[Dict[str, Any]]
```

---

## AgentStorm

Parallel multi-agent execution pattern.

### Module

```python
from integrations.agent_storm import AgentStorm, AgentStormConfig, AgentRole
```

### Configuration

```python
@dataclass
class AgentStormConfig:
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    num_agents: int = 4
    max_workers: int = 4
    synthesizer_model: str = "qwen2.5-coder"
    timeout: int = 300
```

### AgentRole

```python
@dataclass
class AgentRole:
    name: str
    system_prompt: str
    focus: str
```

### Constructor

```python
AgentStorm(config: Optional[AgentStormConfig] = None)
```

### Methods

#### storm

Run Agent Storm - parallel execution of multiple agents.

```python
def storm(
    self,
    task: str,
    prompt: str,
    num_agents: Optional[int] = None,
    custom_roles: Optional[List[AgentRole]] = None,
) -> Dict[str, Any]
```

**Parameters:**
- `task` (str): Main task description
- `prompt` (str): Detailed prompt for agents
- `num_agents` (Optional[int]): Number of agents to spawn
- `custom_roles` (Optional[List[AgentRole]]): Optional custom agent roles

**Returns:**
```python
{
    "success": bool,
    "task": str,
    "num_agents": int,
    "duration_seconds": float,
    "individual_results": List[Dict[str, Any]],
    "synthesis": {
        "timestamp": str,
        "synthesis": str,
        "input_count": int,
    },
}
```

**Example:**
```python
storm = AgentStorm()

result = storm.storm(
    task="Design a user authentication system",
    prompt="Create a comprehensive solution with security best practices",
    num_agents=4,
)

print(f"Completed in {result['duration_seconds']:.2f}s")
print(result['synthesis']['synthesis'])
```

#### storm_with_roles

Run Agent Storm with specific role names.

```python
def storm_with_roles(
    self,
    task: str,
    prompt: str,
    roles: List[str],
) -> Dict[str, Any]
```

**Parameters:**
- `task` (str): Main task description
- `prompt` (str): Detailed prompt for agents
- `roles` (List[str]): List of role names ("architect", "backend", "security", etc.)

**Example:**
```python
result = storm.storm_with_roles(
    task="Implement REST API for user management",
    prompt="Create CRUD operations with proper validation",
    roles=["backend", "security", "testing"],
)
```

#### parallel_tasks

Execute multiple subtasks in parallel using specialized agents.

```python
def parallel_tasks(
    self,
    task: str,
    subtasks: List[str],
) -> Dict[str, Any]
```

**Parameters:**
- `task` (str): Main task description
- `subtasks` (List[str]): List of subtasks to execute in parallel

**Returns:**
```python
{
    "success": bool,
    "task": str,
    "num_subtasks": int,
    "duration_seconds": float,
    "results": List[Dict[str, Any]],
}
```

**Example:**
```python
result = storm.parallel_tasks(
    task="Build user management feature",
    subtasks=[
        "Design database schema",
        "Create API endpoints",
        "Implement authentication",
        "Write tests",
    ],
)

for r in result['results']:
    print(f"{r['subtask']}: {'✓' if r['success'] else '✗'}")
```

#### get_results

Get all storm results.

```python
def get_results(self) -> List[Dict[str, Any]]
```

#### clear_results

Clear stored results.

```python
def clear_results(self) -> None
```

### Default Agent Roles

| Role | Focus |
|------|-------|
| `architect` | System design and architecture |
| `backend` | API, database, business logic |
| `security` | Vulnerabilities, auth, compliance |
| `testing` | Test coverage and quality |
| `frontend` | UI components and UX |
| `devops` | Infrastructure and deployment |

---

## Error Handling

All agents follow consistent error handling patterns:

### Success Response

```python
{
    "success": True,
    # ... additional fields
}
```

### Error Response

```python
{
    "success": False,
    "error": str,  # Error message
    # ... additional context
}
```

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| `ImportError` | Missing dependency | Install required package |
| `TimeoutError` | Operation timed out | Increase timeout value |
| `ValueError` | Invalid parameter | Check parameter values |
| `ConnectionError` | Cannot connect to Ollama | Start Ollama server |
