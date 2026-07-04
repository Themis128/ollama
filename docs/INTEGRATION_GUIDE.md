# Integration Guide

This guide covers how to integrate and use the DeepAgents + Ollama system with your projects.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Basic Integration](#basic-integration)
4. [Project-Specific Integration](#project-specific-integration)
5. [MCP Server Integration](#mcp-server-integration)
6. [Skills Integration](#skills-integration)
7. [Custom Agents](#custom-agents)
8. [GUI (Terminal-Based Interface)](#gui-terminal-based-interface)

---

## Installation

### Prerequisites

- Python 3.11+
- Ollama (running locally or remotely)
- UV package manager (recommended)

### Step 1: Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Pull the coding model
ollama pull qwen2.5-coder

# Verify installation
ollama list
```

### Step 2: Setup Project Environment

```bash
cd /home/tbaltzakis/ollama

# Create virtual environment
uv venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
uv pip install langchain-ollama langchain-core requests httpx colorama
```

### Step 3: Optional - Install DeepAgents SDK

```bash
# For full DeepAgents integration
uv pip install deepagents
```

### Step 4: Verify Installation

```bash
# Test imports
python -c "
from integrations import TDDAgent, TerminalAgent, SandboxAgent
from integrations import Orchestrator, WebAgent, DebugAgent, AgentStorm
print('All imports successful!')
"

# Start Ollama and test
ollama serve &
sleep 5
curl http://localhost:11434/api/tags
```

---

## Configuration

---

## Installation

### Prerequisites

- Python 3.11+
- Ollama (running locally or remotely)
- UV package manager (recommended)

### Step 1: Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Pull the coding model
ollama pull qwen2.5-coder

# Verify installation
ollama list
```

### Step 2: Setup Project Environment

```bash
cd /home/tbaltzakis/ollama

# Create virtual environment
uv venv .venv

# Activate it
source .venv/bin/activate

# Install dependencies
uv pip install langchain-ollama langchain-core requests httpx
```

### Step 3: Optional - Install DeepAgents SDK

```bash
# For full DeepAgents integration
uv pip install deepagents
```

### Step 4: Verify Installation

```bash
# Test imports
python -c "
from integrations import TDDAgent, TerminalAgent, SandboxAgent
from integrations import Orchestrator, WebAgent, DebugAgent, AgentStorm
print('All imports successful!')
"

# Start Ollama and test
ollama serve &
sleep 5
curl http://localhost:11434/api/tags
```

---

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder

# Agent Configuration
AGENT_TEMPERATURE=0.1
AGENT_MAX_TOKENS=4096
AGENT_TIMEOUT=120

# Project Configuration
PROJECT_PATH=/home/tbaltzakis/your-project

# Web Agent Configuration
WEB_RATE_LIMIT=10
WEB_TIMEOUT=30
WEB_CACHE_DIR=/tmp/web_agent_cache

# Sandbox Configuration
SANDBOX_TIMEOUT=120
SANDBOX_AUDIT_LOG=/tmp/sandbox_audit.log
```

### Configuration Classes

#### TDDConfig

```python
from integrations.tdd_agent import TDDConfig

config = TDDConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/path/to/project",
    temperature=0.1,
    max_iterations=10,
    timeout=60,
)
```

#### TerminalConfig

```python
from integrations.terminal_agent import TerminalConfig

config = TerminalConfig(
    project_path="/path/to/project",
    sandbox=True,
    allowlist=["npm", "pnpm", "git", "python"],
    blocklist=["rm -rf", "sudo"],
    timeout=120,
    max_retries=3,
)
```

#### SandboxConfig

```python
from integrations.sandbox_agent import SandboxConfig

config = SandboxConfig(
    project_path="/path/to/project",
    allow_dangerous=False,
    enable_isolation=True,
    max_output_size=100000,
    timeout=120,
    audit_log_path="/tmp/audit.log",
)
```

#### WebConfig

```python
from integrations.web_agent import WebConfig

config = WebConfig(
    rate_limit=10,
    timeout=30,
    max_retries=3,
    cache_dir="/tmp/cache",
    safe_domains=["docs.example.com", "api.example.com"],
)
```

#### AgentStormConfig

```python
from integrations.agent_storm import AgentStormConfig

config = AgentStormConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    num_agents=4,
    max_workers=4,
    synthesizer_model="qwen2.5-coder",
    timeout=300,
)
```

---

## Basic Integration

### Quick Start

```python
from integrations import (
    TDDAgent,
    TerminalAgent,
    SandboxAgent,
    Orchestrator,
    WebAgent,
    DebugAgent,
    AgentStorm,
)

# Create agents
tdd = TDDAgent()
terminal = TerminalAgent()
sandbox = SandboxAgent()
orchestrator = Orchestrator()
web = WebAgent()
debugger = DebugAgent()
storm = AgentStorm()

# Use them
result = sandbox.execute("echo 'Hello World'")
print(result['stdout'])
```

### Simple Coding Task

```python
from integrations import Orchestrator

orchestrator = Orchestrator()

result = orchestrator.execute(
    task="Create a Python function to calculate fibonacci numbers",
    mode="code",
)

print(result['output'])
```

### With Custom Configuration

```python
from integrations.tdd_agent import TDDAgent, TDDConfig

config = TDDConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/home/tbaltzakis/my-project",
    temperature=0.1,
)

tdd = TDDAgent(config)

result = tdd.run_tdd(
    feature="Add user validation",
    test_file="tests/test_user.py",
    implementation_file="src/user.py",
)
```

---

## Project-Specific Integration

### Integration with Next.js Project

```python
from integrations.orchestrator_agent import Orchestrator, OrchestratorConfig

config = OrchestratorConfig(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    project_path="/home/tbaltzakis/nextjs-app",
)

orchestrator = Orchestrator(config)

# Generate API route
result = orchestrator.execute(
    task="Create a REST API endpoint for user registration",
    mode="auto",
    context={
        "framework": "Next.js 14",
        "language": "TypeScript",
        "database": "PostgreSQL",
        "orm": "Prisma",
    },
)
```

### Integration with Python Project

```python
from integrations.tdd_agent import TDDAgent, TDDConfig

config = TDDConfig(
    model="qwen2.5-coder",
    project_path="/home/tbaltzakis/python-api",
)

tdd = TDDAgent(config)

result = tdd.run_tdd(
    feature="Create FastAPI endpoint for user CRUD",
    test_file="tests/test_users.py",
    implementation_file="app/routers/users.py",
    test_command="pytest tests/",
)
```

### cloudless.gr Integration

```python
from integrations import create_cloudless_agent

# Note: Requires deepagents package
try:
    agent = create_cloudless_agent(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
        project_path="/home/tbaltzakis/cloudless.gr",
    )
    
    result = agent.invoke({
        "messages": "Create a DynamoDB query for user sessions",
        "skill": "database",
    })
except ImportError:
    print("DeepAgents package required for cloudless.gr integration")
```

---

## MCP Server Integration

### What is MCP?

Model Context Protocol (MCP) servers provide tools and resources that agents can use. The cloudless.gr project has 12 MCP servers configured.

### Listing Available MCP Servers

```python
import json
from pathlib import Path

mcp_config_path = Path("/home/tbaltzakis/cloudless.gr/.deepagents/.mcp.json")

if mcp_config_path.exists():
    with open(mcp_config_path) as f:
        config = json.load(f)
    
    servers = list(config.get("mcpServers", {}).keys())
    print("Available MCP Servers:")
    for server in servers:
        print(f"  - {server}")
```

### Common MCP Servers

| Server | Purpose | Tools |
|--------|---------|-------|
| `github` | GitHub API | create_issue, create_pr, search |
| `git` | Git operations | commit, push, pull, branch |
| `filesystem` | File operations | read, write, delete, search |
| `memory` | Context storage | store, recall, forget |
| `sentry` | Error tracking | get_issues, resolve |
| `postgres` | Database queries | query, migrate |
| `aws` | AWS services | s3_upload, lambda_invoke |

### Using MCP Servers

```python
# MCP servers are automatically loaded by DeepAgents SDK
# Tools are exposed to the agent based on server configuration

# Example with filesystem MCP
result = agent.invoke({
    "messages": "Read the package.json file and suggest improvements",
    "tools": ["filesystem.read", "filesystem.write"],
})
```

---

## Skills Integration

### What are Skills?

Skills are specialized capabilities that can be invoked by agents. The cloudless.gr project has 8 custom skills.

### Available Skills

| Skill | Purpose | Example Use |
|-------|---------|-------------|
| `code-review` | Review code quality | "Review the auth module" |
| `database` | Database operations | "Optimize this query" |
| `deploy` | Deployment tasks | "Deploy to staging" |
| `git-workflow` | Git operations | "Create feature branch" |
| `monitoring` | System monitoring | "Check error rates" |
| `performance` | Performance optimization | "Profile this function" |
| `security` | Security analysis | "Audit auth flow" |
| `test` | Testing operations | "Generate test cases" |

### Using Skills

```python
# Skills are project-specific and loaded from .deepagents/skills/

# List available skills
import os
from pathlib import Path

skills_dir = Path("/home/tbaltzakis/cloudless.gr/.deepagents/skills")
if skills_dir.exists():
    skills = [d for d in os.listdir(skills_dir) if (skills_dir / d).is_dir()]
    print(f"Available skills: {skills}")

# Use a skill (requires DeepAgents SDK)
result = agent.invoke({
    "messages": "Review the authentication implementation",
    "skill": "code-review",
})
```

### Creating Custom Skills

```bash
# Create skill directory
mkdir -p /path/to/project/.deepagents/skills/my-skill

# Create skill prompt
cat > /path/to/project/.deepagents/skills/my-skill/prompt.md << 'EOF'
# My Custom Skill

You are an expert in [DOMAIN].

## Capabilities:
- Capability 1
- Capability 2

## Guidelines:
1. Guideline 1
2. Guideline 2
EOF
```

---

## Custom Agents

### Creating a Custom Agent Role

```python
from integrations.agent_storm import AgentRole, AgentStorm, AgentStormConfig

# Define custom role
custom_role = AgentRole(
    name="api-designer",
    system_prompt="""You are an API Design Expert.

Your focus:
- RESTful API best practices
- OpenAPI specification
- Versioning strategies
- Rate limiting and caching
- Authentication patterns

When designing APIs:
1. Follow REST principles
2. Use consistent naming conventions
3. Version your APIs
4. Document all endpoints
5. Handle errors gracefully""",
    focus="API design and documentation",
)

# Use in Agent Storm
config = AgentStormConfig(num_agents=1)
storm = AgentStorm(config)

result = storm.storm(
    task="Design a public API for user management",
    prompt="Create OpenAPI 3.0 specification",
    custom_roles=[custom_role],
)
```

### Creating a Specialized Agent

```python
from langchain_ollama import ChatOllama
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class MyAgentConfig:
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    temperature: float = 0.1
    custom_prompt: str = ""

class MyCustomAgent:
    """Custom agent for specific use case."""
    
    def __init__(self, config: Optional[MyAgentConfig] = None):
        self.config = config or MyAgentConfig()
        self.llm = ChatOllama(
            model=self.config.model,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
        )
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute task with custom logic."""
        
        prompt = f"""{self.config.custom_prompt}

TASK: {task}

Execute the task following your specialized guidelines."""
        
        if context:
            prompt += f"\n\nContext:\n{context}"
        
        response = self.llm.invoke(prompt)
        
        return {
            "success": True,
            "output": response.content,
            "task": task,
        }

# Usage
config = MyAgentConfig(
    custom_prompt="You are a database optimization expert...",
)

agent = MyCustomAgent(config)
result = agent.execute("Optimize this SQL query: SELECT * FROM users")
```

### Extending TDD Agent

```python
from integrations.tdd_agent import TDDAgent, TDDConfig
from typing import Dict, Any

class ExtendedTDDAgent(TDDAgent):
    """Extended TDD agent with custom features."""
    
    def run_tdd_with_docs(
        self,
        feature: str,
        test_file: str,
        implementation_file: str,
        docs_file: str,
        test_command: str = "pnpm test",
    ) -> Dict[str, Any]:
        """Run TDD cycle and generate documentation."""
        
        # Run standard TDD cycle
        result = self.run_tdd(feature, test_file, implementation_file, test_command)
        
        if result["status"] == "success":
            # Generate documentation
            doc_prompt = f"""Generate JSDoc/TSDoc documentation for:

FEATURE: {feature}

IMPLEMENTATION:
{self._read_file(implementation_file)}

Generate comprehensive documentation with:
- Function descriptions
- Parameter documentation
- Return type documentation
- Usage examples"""
            
            docs = self.llm.invoke(doc_prompt)
            self._write_file(docs_file, docs.content)
            
            result["docs_file"] = docs_file
        
        return result

# Usage
agent = ExtendedTDDAgent()
result = agent.run_tdd_with_docs(
    feature="User authentication",
    test_file="src/auth.test.ts",
    implementation_file="src/auth.ts",
    docs_file="src/auth.md",
)
```

---

## Integration Examples

### Example 1: Full Development Workflow

```python
from integrations import (
    TDDAgent,
    TerminalAgent,
    SandboxAgent,
    Orchestrator,
    WebAgent,
    AgentStorm,
)

# 1. Research
web = WebAgent()
research = web.research("Next.js middleware authentication", sources=3)

# 2. Design
storm = AgentStorm()
design = storm.storm_with_roles(
    task="Design authentication middleware",
    prompt="Based on research findings",
    roles=["architect", "security"],
)

# 3. Implement with TDD
tdd = TDDAgent()
impl = tdd.run_tdd(
    feature="JWT authentication middleware",
    test_file="src/middleware/auth.test.ts",
    implementation_file="src/middleware/auth.ts",
)

# 4. Verify
sandbox = SandboxAgent()
test_result = sandbox.execute("pnpm test")
build_result = sandbox.execute("pnpm build")

# 5. Deploy (if tests pass)
if test_result['success'] and build_result['success']:
    deploy_result = sandbox.execute("pnpm deploy:staging")
    print(f"Deployed: {deploy_result['success']}")
```

### Example 2: Code Review Workflow

```python
from integrations import AgentStorm, TerminalAgent, DebugAgent

# 1. Run tests
terminal = TerminalAgent()
test_result = terminal.execute("pnpm test")

# 2. If failures, analyze
if not test_result['success']:
    debugger = DebugAgent()
    diagnosis = debugger.analyze_error(
        test_result['stderr'],
        file_path=None,
    )
    print(f"Issues found: {diagnosis['severity']}")

# 3. Get review from multiple perspectives
storm = AgentStorm()
review = storm.storm_with_roles(
    task="Review code quality",
    prompt="Analyze codebase for issues",
    roles=["architect", "security", "testing"],
)

print(review['synthesis']['synthesis'])
```

### Example 3: Automated Bug Fix

```python
from integrations import DebugAgent, SandboxAgent, TerminalAgent

# 1. Detect error
terminal = TerminalAgent()
result = terminal.execute("pnpm test")

if not result['success']:
    # 2. Analyze error
    debugger = DebugAgent()
    diagnosis = debugger.analyze_error(result['stderr'])
    
    # 3. Generate fix
    fix = debugger.generate_fix(
        result['stderr'],
        file_path=diagnosis['location']['file'],
    )
    
    # 4. Apply fix (would need file writing capability)
    print(f"Fix generated for {diagnosis['location']['file']}")
    print(f"Suggestion: {diagnosis['suggested_fix']}")
    
    # 5. Re-run tests
    result = terminal.execute("pnpm test")
    print(f"Tests pass: {result['success']}")
```

---

## Troubleshooting

### Common Issues

#### 1. Ollama Connection Failed

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull model if not available
ollama pull qwen2.5-coder
```

#### 2. Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
uv pip install --reinstall langchain-ollama langchain-core
```

#### 3. Command Blocked in Sandbox

```python
# Check why command was blocked
sandbox = SandboxAgent()
result = sandbox.execute("some-command")

if not result['success']:
    print(result.get('error', 'Unknown error'))
    
    # Check audit log
    for entry in sandbox.get_audit_log():
        if entry['type'] == 'BLOCKED':
            print(f"Blocked: {entry['command']}")
            print(f"Reason: {entry['reason']}")
```

#### 4. Rate Limited in Web Agent

```python
# Increase rate limit
from integrations.web_agent import WebConfig

config = WebConfig(rate_limit=30)  # 30 requests per minute
web = WebAgent(config)
```

### Getting Help

1. Check the [ARCHITECTURE.md](ARCHITECTURE.md) for system design
2. Check the [WORKFLOWS.md](WORKFLOWS.md) for usage patterns
3. Review the audit logs at `/tmp/sandbox_audit.log`
4. Check Ollama logs for model issues
