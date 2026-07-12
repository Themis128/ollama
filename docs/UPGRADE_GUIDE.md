# Infrastructure Upgrade & Agent Improvement Guide

Guide for upgrading the DeepAgents + Ollama infrastructure and improving agent capabilities.

## 🚀 Infrastructure Upgrade Paths

### 1. Ollama Backend Enhancements

#### Upgrade to Newer Models
```bash
# Check current model
ollama list

# Pull improved models
ollama pull qwen2.5-coder:72b    # Larger for better reasoning
ollama pull qwen2.5-coder:32b    # Balanced option
ollama pull llama3.3:latest       # Latest Llama
ollama pull deepseek-coder:latest  # Specialized for code

# Test new model
OLLAMA_MODEL=llama3.3 ./scripts/ollama-agent.sh "Explain this codebase"
```

#### Ollama Server Optimization
```bash
# For GPU acceleration (NVIDIA)
docker run -d --gpus all -v ollama:/root/.ollama -p 11434:11434 ollama/ollama:latest

# For memory-constrained systems
export OLLAMA_MAX_MODEL_SIZE=8GB  # Limit model size
export OLLAMA_FLASH_ATTENTION=1   # Enable flash attention

# Multi-model setup
# Configure different models for different tasks:
# - qwen2.5-coder for general coding
# - llama3.2:vision for image understanding
# - deepseek-coder for pure code tasks
```

### 2. Cloud Infrastructure

#### Cloudflare Workers Migration
```bash
# Current: Local Ollama only
# Upgrade: Hybrid Cloudflare + Ollama

# 1. Set up Cloudflare deployment
cd /home/tbaltzakis/cloudless.gr
pnpm install

# 2. Configure AI Gateway
# Add to .env.local:
echo "CF_AI_GATEWAY=https://gateway.ai.cloudflare.com" >> .env.local
echo "OLLAMA_BASE_URL=http://localhost:11434/v1" >> .env.local

# 3. Enable Cloudflare skills
./scripts/setup-cloudflare-skills.sh
```

#### MCP Server Enhancements
```python
# Add new MCP servers to .deepagents/.mcp.json:
{
  "mcpServers": {
    "cloudflare": {"url": "https://mcp.cloudflare.com/mcp"},
    "github": {"command": "uvx mcp-server-github"},
    "filesystem": {"command": "npx @modelcontextprotocol/server-filesystem"},
    "postgres": {"command": "npx @modelcontextprotocol/server-postgres"},
    "redis": {"command": "npx @modelcontextprotocol/server-redis"}
  }
}
```

### 3. Database & Vector Storage

#### Add Vector Memory
```python
# Add to integrations:
from integrations.custom_tools import create_tool

vector_memory = create_tool(
    name="vector_store",
    description="Store and retrieve embeddings for long-term memory",
    input_schema={
        "action": (str, "store or retrieve"),
        "text": (str, "Text to embed"),
        "namespace": (str, "Memory namespace")
    },
    execute=lambda input, ctx: store_embedding(
        input["text"], 
        input.get("namespace", "default")
    )
)
```

---

## 🛠️ Agent Improvements

### 1. Enhanced NLP Processing

#### Add More Intent Patterns
```python
# Extend integrations/nlp_processor.py:
class Intent(Enum):
    ANALYZE = "analyze"
    CODE = "code"
    TEST = "test"
    RESEARCH = "research"
    REFACTOR = "refactor"      # NEW
    DEPLOY = "deploy"          # NEW
    DOCUMENT = "document"      # NEW
    REVIEW = "review"          # NEW

# Add patterns with higher precision:
intent_patterns = {
    Intent.REFACTOR: [
        (r"\b(refactor|optimize|cleanup|simplify)\b", 0.95),
        (r"\b(improve|enhance) (code|function|module)\b", 0.9),
    ],
    Intent.DOCUMENT: [
        (r"\b(document|comment|explain)\s+(function|code|api)\b", 0.9),
        (r"\b(add|write) (docs|documentation|comments)\b", 0.9),
    ],
}
```

### 2. Tool Enhancements

#### Add Code Analysis Tools
```python
# Add to integrations/custom_tools.py:
def _execute_code_lint(input, context):
    """Run ESLint/TypeScript compiler on codebase."""
    import subprocess
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        capture_output=True,
        cwd=os.environ.get("PROJECT_PATH", ".")
    )
    return ToolResult(output={"lint": result.stdout.decode()})

lint_tool = create_tool(
    name="code_lint",
    description="Run linter on the codebase and return issues",
    input_schema={"fix": (bool, "Auto-fix issues")},
    execute=_execute_code_lint
)
```

### 3. Multi-Agent Pattern Improvements

#### Persistent Agent State
```python
# Add to AgentStorm for state persistence:
from pathlib import Path
import pickle

class AgentStorm:
    def save_state(self, filepath: str = ".agent_storm_state.pkl"):
        """Save storm results for later reference."""
        Path(filepath).write_bytes(pickle.dumps({
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }))
    
    def load_state(self, filepath: str = ".agent_storm_state.pkl"):
        """Load previous storm results."""
        data = pickle.loads(Path(filepath).read_bytes())
        self.results = data["results"]
```

---

## 🔧 Technical Improvements

### 1. Caching Layer

```python
# Add Redis caching to WebAgent:
def _cache_with_redis(self, key: str, value: str, ttl: int = 3600):
    """Cache with Redis for multi-process sharing."""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        r.setex(key, ttl, value)
    except ImportError:
        # Fallback to file cache
        self._cache(key, value)
```

### 2. Async Support

```python
# Update agents for async execution:
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncTDDAgent(TDDAgent):
    async def run_tdd_async(self, feature, test_file, impl_file):
        """Async TDD loop for better performance."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            # Run LLM calls in parallel
            test_future = loop.run_in_executor(
                executor, self._write_failing_test, feature, test_file, impl_file
            )
            # Continue with async operations
            ...
```

### 3. Structured Logging

```python
# Add to all agents:
import structlog

logger = structlog.get_logger()

class TDDAgent:
    def __init__(self, config):
        self.logger = logger.new(agent="tdd", model=config.model)
    
    def run_tdd(self, feature, test_file, impl_file):
        self.logger.info("tdd_cycle_started", feature=feature)
        # ... implementation
        self.logger.info("tdd_cycle_completed", iterations=self.iteration_count)
```

---

## 📊 Performance Optimizations

### 1. Model Routing

```python
# Route tasks to optimal models:
MODEL_ROUTING = {
    "code_generation": "qwen2.5-coder",
    "debugging": "qwen2.5-coder",
    "architecture": "llama3.3",
    "documentation": "llama3.2",
    "security_review": "deepseek-coder",
}

def get_optimal_model(task_type: str) -> str:
    return MODEL_ROUTING.get(task_type, "qwen2.5-coder")
```

### 2. Parallel Execution Enhancement

```python
# Use ProcessPoolExecutor for LLM calls:
from concurrent.futures import ProcessPoolExecutor

def _execute_parallel(self, prompts):
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(self._call_llm, p) for p in prompts]
        return [f.result() for f in futures]
```

---

## 🔄 Upgrade Checklist

- [ ] **Ollama**: Pull latest models, configure GPU
- [ ] **Skills**: Run `setup-cloudflare-skills.sh`
- [ ] **MCP**: Add new MCP servers to config
- [ ] **Memory**: Add vector storage for long-term context
- [ ] **NLP**: Extend intent patterns for refactoring/deploy
- [ ] **Tools**: Add code analysis and documentation tools
- [ ] **Performance**: Implement async and caching layers
- [ ] **Logging**: Add structured logging to all modules
- [ ] **Testing**: Run `test-all-tools.py` to verify

---

## 📈 Monitoring & Observability

```python
# Add to agents for metrics:
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('agent_requests', 'Agent requests', ['agent', 'model'])
REQUEST_LATENCY = Histogram('agent_latency', 'Request latency', ['agent'])

class Orchestrator:
    @REQUEST_LATENCY.labels(agent='orchestrator').time()
    def execute(self, task, mode, context):
        REQUEST_COUNT.labels(agent='orchestrator', model=self.config.model).inc()
        # ... implementation