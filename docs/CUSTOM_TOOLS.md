# Custom Tools

Define, register, and test your own tools with type-safe schemas and execution handlers.

Custom tools extend what your agent can do. A tool is a function with a name, a description the LLM reads, a schema for inputs, and an execute function that does the actual work.

## Basic Tool

Use `create_tool` with a schema dict for the simplest approach:

```python
from integrations import create_tool, ToolResult, AgentToolContext
from datetime import datetime

get_current_time = create_tool(
    name="get_current_time",
    description="Get the current date and time. Optionally specify a timezone.",
    input_schema={
        "timezone": (str, "IANA timezone (e.g., 'America/New_York'). Defaults to UTC."),
    },
    execute=lambda input, context: ToolResult(output={
        "iso": datetime.now().isoformat(),
        "timezone": input("timezone", "UTC"),
        "formatted": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }),
)
```

The SDK converts the schema to JSON Schema automatically via `to_json_schema()`. Input is fully typed in the execute function.

For working examples of tools in real agents, see:
- `integrations/custom_tools.py` - Core implementation
- `tests/test_custom_tools.py` - Test examples

## Anatomy of a Tool

Every tool has four parts:

| Field | Purpose |
|-------|---------|
| `name` | Unique identifier (snake_case recommended) |
| `description` | LLM reads this to decide when to use the tool |
| `input_schema` | Dict mapping field names to `(type, description)` tuples |
| `execute` | Function that does the work |

### The Name

Use snake_case. Keep it descriptive but concise:

```python
# Good examples
search_database = create_tool(name="search_database", ...)  # NOT "db" or "performDatabaseSearchOperation"
send_email = create_tool(name="send_email", ...)          # NOT "email" or "handleEmailSending"
shell = create_tool(name="shell", ...)                    # NOT "exec" or "runCommand"
```

### The Description

This is the most important field for tool call accuracy. The LLM uses it to decide when and how to use the tool.

```python
# Weak: model won't know when to use this
description="Handles data."

# Strong: model knows exactly what this does and when to use it
description="Generate text using Ollama LLM. Sends a prompt to the specified model and returns the generated response. "
            "Use this for code generation, analysis, and general queries. Model runs locally - no API costs. "
            "Maximum 100 rows per query."

# Include:
# - What the tool does
# - What it returns
# - When to use it (and when not to)
# - Constraints (rate limits, read-only, max results, etc.)
```

### The Input Schema

With Python, define field types and descriptions in a tuple:

```python
input_schema={
    "query": (str, "Search query. Supports wildcards (*) and exact phrases."),
    "limit": (int, "Maximum results to return. Default: 10."),
    "status": (str, "Filter by record status. One of: active, archived, deleted."),
},
```

Use type hints in the description for fields with a fixed set of values. This dramatically improves accuracy.

## Using AgentToolContext

The execute function receives a context object with execution metadata:

```python
import asyncio

async def long_process(input: dict, context: AgentToolContext) -> ToolResult:
    """Process data in batches."""
    print(f"Agent: {context.agent_id}, Iteration: {context.iteration}")

    for batch in batches:
        # Check for cancellation signal
        if context.signal and hasattr(context.signal, "aborted") and context.signal.aborted:
            return ToolResult(output={"status": "cancelled", "processed": count})
        await process_batch(batch)

    return ToolResult(output={"status": "complete"})
```

## Error Handling

Return errors as structured data rather than raising:

```python
def api_tool(input: dict, context: AgentToolContext) -> ToolResult:
    """Make an authenticated API call."""
    try:
        response = urllib.request.urlopen(...)
        
        if response.status != 200:
            return ToolResult(
                output={"error": f"API returned {response.status}"},
                is_error=True,
            )

        return ToolResult(output={"data": response.json()})
    except Exception as e:
        return ToolResult(
            output={"error": f"Network error: {str(e)}"},
            is_error=True,
        )
```

When a tool returns an error, the agent sees it and can adjust its approach. When a tool throws, it counts as a "mistake" and increments the consecutive mistake counter.

## Completion Tools

Mark a tool with `lifecycle={"completes_run": True}` to make it end the agent loop when called successfully:

```python
submit_result = create_tool(
    name="submit_result",
    description="Submit the final result and end the run.",
    input_schema={
        "summary": (str, "Summary of what was accomplished."),
        "approved": (bool, "Whether the result was approved."),
    },
    lifecycle={"completes_run": True},
    execute=lambda input, context: ToolResult(output=input),
)
```

See the custom_tools implementation for this pattern in a complete application.

## Testing Tools

Test your tools in isolation before giving them to an agent:

```python
# tests/test_my_tool.py
from integrations import create_tool, ToolResult, AgentToolContext

def test_my_tool():
    registry = ToolRegistry()
    registry.register(my_custom_tool)

    context = AgentToolContext(
        agent_id="test",
        run_id="run_test",
        iteration=1,
        tool_call_id="tool_test",
        signal=None,
    )

    result = registry.execute_tool("my_tool", {"input": "test"}, context)

    assert not result.is_error
    assert "expected_key" in result.output
```

## Registering Tools

### Via Registry

```python
from integrations import create_tool, ToolRegistry, ToolResult, AgentToolContext

# Create a registry with your tools
registry = ToolRegistry()
registry.register(my_tool)
registry.register(another_tool)

# Execute a tool
context = AgentToolContext(...)
result = registry.execute_tool("my_tool", {"param": "value"}, context)
```

### Via Agent

```python
from integrations import Orchestrator

# Pass extra tools to orchestrator
orchestrator = Orchestrator(
    model="qwen2.5-coder",
    extra_tools=[my_tool, another_tool],  # If Orchestrator supports this
)
```

## Built-in Tools

The default registry includes these ready-to-use tools:

| Tool | Description |
|------|-------------|
| `get_time` | Get current date and time with timezone support |
| `ollama_generate` | Generate text using local Ollama models |
| `file_read` | Read file contents from filesystem |
| `file_write` | Write content to files, creating directories if needed |
| `shell` | Execute shell commands safely |
| `submit_result` | Submit final result and complete the run |

### Using Built-in Tools

```python
from integrations import get_default_registry

registry = get_default_registry()

# Get current time
result = registry.execute_tool("get_time", {"timezone": "Europe/Athens"})
print(result.output)
# {"iso": "2026-12-07T18:04:00.000000", "timestamp": "2026-12-07 18:04:00", "timezone": "Europe/Athens"}

# List available tools
print(registry.list_tools())
# ["get_time", "ollama_generate", "file_read", "file_write", "shell", "submit_result"]
```

### CLI Usage

```bash
# Get current time
python -m integrations.custom_tools get_time --param timezone=UTC

# Read a file
python -m integrations.custom_tools file_read --param filepath=README.md

# Write a file
python -m integrations.custom_tools file_write --param filepath=output.txt --param content="Hello"

# Run a shell command
python -m integrations.custom_tools shell --param command="echo hello"
```

## Tool Design Rules

Good tools are specific and predictable:

- [x] Use action-oriented names: `get_time`, `shell`, `file_read`
- [x] Describe what the tool does, when to use it, and what it returns
- [x] Put constraints in the description: rate limits, read-only behavior, required permissions
- [x] Add descriptions for every input property
- [x] Return structured JSON instead of prose when possible
- [x] Respect context.signal in long-running tools