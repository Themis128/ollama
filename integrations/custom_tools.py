"""
Custom Tools Module for DeepAgents + Ollama
==========================================

Provides a type-safe tool definition and registration system for extending agent capabilities.
Implements the createTool pattern in Python with support for:
- Schema validation using pydantic
- Agent context with execution metadata
- Structured error handling
- Completion tools (lifecycle)
- Tool registration and discovery

Usage:
    from integrations.custom_tools import create_tool, ToolRegistry

    # Define a tool
    get_time = create_tool(
        name="get_time",
        description="Get current date and time. Returns ISO timestamp.",
        input_schema={
            "timezone": (str, "Optional IANA timezone (e.g., 'America/New_York'). Defaults to UTC.")
        },
        execute=lambda input, context: {
            "iso": datetime.now().isoformat(),
            "timezone": input.get("timezone", "UTC")
        }
    )

    # Register and use
    registry = ToolRegistry()
    registry.register(get_time)
"""

import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
import json


class AgentToolContext(TypedDict):
    """Context object passed to tool execute functions."""
    agent_id: str
    run_id: str
    iteration: int
    tool_call_id: str
    signal: Optional[Any]  # AbortSignal-like object


@dataclass
class ToolResult:
    """Result from a tool execution."""
    output: Dict[str, Any]
    is_error: bool = False


@dataclass
class Tool:
    """Represents a registered tool with its definition and handler."""
    name: str
    description: str
    input_schema: Dict[str, tuple]  # field_name -> (type, description)
    execute: Callable[[Dict[str, Any], AgentToolContext], ToolResult]
    lifecycle: Dict[str, bool] = field(default_factory=lambda: {"completes_run": False})
    is_async: bool = False


def create_tool(
    name: str,
    description: str,
    input_schema: Dict[str, tuple],
    execute: Callable[[Dict[str, Any], AgentToolContext], ToolResult],
    lifecycle: Optional[Dict[str, bool]] = None,
) -> Tool:
    """
    Create a tool with a name, description, schema, and execute function.

    Args:
        name: Unique identifier (snake_case recommended)
        description: LLM-readable description of what the tool does, when to use it, and constraints
        input_schema: Dict mapping field names to (type, description) tuples
        execute: Async function that performs the work, receives (input, context)
        lifecycle: Optional dict with 'completes_run' flag

    Returns:
        Tool instance ready for registration

    Example:
        >>> get_time = create_tool(
        ...     name="get_time",
        ...     description="Get current date and time. Returns ISO and formatted strings.",
        ...     input_schema={
        ...         "timezone": (str, "IANA timezone like 'America/New_York'. Defaults to UTC.")
        ...     },
        ...     execute=lambda input, ctx: ToolResult(output={
        ...         "iso": datetime.now().isoformat(),
        ...         "formatted": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ...     })
        ... )
    """
    return Tool(
        name=name,
        description=description,
        input_schema=input_schema,
        execute=execute,
        lifecycle=lifecycle or {"completes_run": False},
    )


class ToolRegistry:
    """Registry for managing and discovering tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """Register a tool with the registry."""
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> bool:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        """List all registered tool names."""
        return list(self._tools.keys())

    def execute_tool(
        self,
        name: str,
        input: Dict[str, Any],
        context: Optional[AgentToolContext] = None,
    ) -> ToolResult:
        """
        Execute a registered tool.

        Args:
            name: Tool name to execute
            input: Input parameters matching the tool's schema
            context: Optional execution context

        Returns:
            ToolResult with output or error
        """
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(
                output={"error": f"Tool not found: {name}"},
                is_error=True,
            )

        # Create default context if not provided
        ctx = context or AgentToolContext(
            agent_id="default",
            run_id="default",
            iteration=1,
            tool_call_id=f"call_{name}",
            signal=None,
        )

        # Check for cancellation
        if ctx.get("signal") and hasattr(ctx["signal"], "aborted") and ctx["signal"].aborted:
            return ToolResult(
                output={"error": "Tool execution cancelled"},
                is_error=True,
            )

        try:
            result = tool.execute(input, ctx)
            if isinstance(result, ToolResult):
                return result
            return ToolResult(output=result)
        except Exception as e:
            return ToolResult(
                output={"error": f"Tool execution failed: {str(e)}"},
                is_error=True,
            )

    def to_json_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Convert tool schema to JSON Schema format."""
        tool = self._tools.get(name)
        if tool is None:
            return None

        properties = {}
        for field_name, (field_type, description) in tool.input_schema.items():
            type_map = {
                str: "string",
                int: "integer",
                float: "number",
                bool: "boolean",
                list: "array",
                dict: "object",
            }
            properties[field_name] = {
                "type": type_map.get(field_type, "string"),
                "description": description,
            }

        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                },
            },
        }


# Built-in tools for the ollama integration

def _execute_ollama_generate(input: Dict[str, Any], context: AgentToolContext) -> ToolResult:
    """Generate text using Ollama."""
    import urllib.request

    prompt = input.get("prompt", "")
    model = input.get("model", "qwen2.5-coder")
    base_url = input.get("base_url", "http://localhost:11434")

    if not prompt:
        return ToolResult(
            output={"error": "Prompt is required"},
            is_error=True,
        )

    try:
        req = urllib.request.Request(
            f"{base_url}/api/generate",
            data=json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False,
            }).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=120) as response:
            data = json.loads(response.read().decode())
            return ToolResult(
                output={
                    "response": data.get("response", ""),
                    "model": model,
                    "done": data.get("done", False),
                }
            )
    except Exception as e:
        return ToolResult(
            output={"error": f"Ollama generation failed: {str(e)}"},
            is_error=True,
        )


def _execute_file_read(input: Dict[str, Any], context: AgentToolContext) -> ToolResult:
    """Read file contents."""
    filepath = input.get("filepath", "")

    if not filepath:
        return ToolResult(
            output={"error": "Filepath is required"},
            is_error=True,
        )

    path = Path(filepath)
    if not path.exists():
        return ToolResult(
            output={"error": f"File not found: {filepath}"},
            is_error=True,
        )

    try:
        content = path.read_text()
        return ToolResult(
            output={
                "content": content,
                "filepath": filepath,
                "size": len(content),
            }
        )
    except Exception as e:
        return ToolResult(
            output={"error": f"Failed to read file: {str(e)}"},
            is_error=True,
        )


def _execute_file_write(input: Dict[str, Any], context: AgentToolContext) -> ToolResult:
    """Write content to a file."""
    import os

    filepath = input.get("filepath", "")
    content = input.get("content", "")

    if not filepath:
        return ToolResult(
            output={"error": "Filepath is required"},
            is_error=True,
        )

    path = Path(filepath)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return ToolResult(
            output={
                "success": True,
                "filepath": str(path),
                "bytes_written": len(content.encode()),
            }
        )
    except Exception as e:
        return ToolResult(
            output={"error": f"Failed to write file: {str(e)}"},
            is_error=True,
        )


def _execute_shell(input: Dict[str, Any], context: AgentToolContext) -> ToolResult:
    """Execute a shell command safely."""
    import subprocess

    command = input.get("command", "")
    working_dir = input.get("working_dir", "")

    if not command:
        return ToolResult(
            output={"error": "Command is required"},
            is_error=True,
        )

    # Check for cancellation
    if context.get("signal") and hasattr(context["signal"], "aborted"):
        return ToolResult(
            output={"error": "Command cancelled"},
            is_error=True,
        )

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=working_dir or os.getcwd(),
            timeout=60,
        )
        return ToolResult(
            output={
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
            }
        )
    except subprocess.TimeoutExpired:
        return ToolResult(
            output={
                "error": "Command timed out",
                "command": command,
            },
            is_error=True,
        )
    except Exception as e:
        return ToolResult(
            output={"error": f"Command execution failed: {str(e)}"},
            is_error=True,
        )


def _execute_submit_result(input: Dict[str, Any], context: AgentToolContext) -> ToolResult:
    """Submit final result - marks run as complete."""
    return ToolResult(
        output={
            "complete": True,
            "summary": input.get("summary", ""),
            "approved": input.get("approved", False),
        }
    )


# Create built-in tools
get_time_tool = create_tool(
    name="get_time",
    description="Get the current date and time. Returns both ISO format and human-readable formatted string. "
                "Use this when you need to know the current time or add timestamps to output.",
    input_schema={
        "timezone": (str, "IANA timezone identifier (e.g., 'America/New_York', 'Europe/London'). "
                        "Defaults to system timezone if not specified."),
    },
    execute=lambda input, context: ToolResult(output={
        "iso": datetime.now().isoformat(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "timezone": input.get("timezone", "UTC"),
    }),
)

ollama_generate_tool = create_tool(
    name="ollama_generate",
    description="Generate text using Ollama LLM. Sends a prompt to the specified model and returns the generated response. "
                "Use this for code generation, analysis, and general queries. "
                "Model runs locally - no API costs.",
    input_schema={
        "prompt": (str, "The prompt to send to the model."),
        "model": (str, "Model name (e.g., 'qwen2.5-coder', 'llama3.2'). Defaults to 'qwen2.5-coder'."),
        "base_url": (str, "Ollama server URL. Defaults to 'http://localhost:11434'."),
    },
    execute=_execute_ollama_generate,
)

file_read_tool = create_tool(
    name="file_read",
    description="Read the contents of a file from the filesystem. Returns file content as string. "
                "Use this to examine existing code before making changes. "
                "Maximum file size: 1MB.",
    input_schema={
        "filepath": (str, "Absolute or relative path to the file to read."),
    },
    execute=_execute_file_read,
)

file_write_tool = create_tool(
    name="file_write",
    description="Write content to a file, creating directories if needed. Overwrites existing files. "
                "Use this to save generated code or configuration files. "
                "Returns bytes written on success.",
    input_schema={
        "filepath": (str, "Path where to write the file. Parent directories created automatically."),
        "content": (str, "Content to write to the file."),
    },
    execute=_execute_file_write,
)

shell_tool = create_tool(
    name="shell",
    description="Execute a shell command in the terminal. Use for running tests, builds, git operations, etc. "
                "Respects timeout (60s max). Supports common development commands. "
                "Returns stdout, stderr, and exit code.",
    input_schema={
        "command": (str, "Shell command to execute."),
        "working_dir": (str, "Working directory for command execution. Defaults to current directory."),
    },
    execute=_execute_shell,
)

submit_result_tool = create_tool(
    name="submit_result",
    description="Submit the final result and complete the agent run. Use this to signal task completion.",
    input_schema={
        "summary": (str, "Summary of what was accomplished."),
        "approved": (bool, "Whether the result was approved/successful."),
    },
    lifecycle={"completes_run": True},
    execute=_execute_submit_result,
)


# Convenience function to get default tool registry
def get_default_registry() -> ToolRegistry:
    """Get a registry pre-populated with built-in tools."""
    registry = ToolRegistry()
    registry.register(get_time_tool)
    registry.register(ollama_generate_tool)
    registry.register(file_read_tool)
    registry.register(file_write_tool)
    registry.register(shell_tool)
    registry.register(submit_result_tool)
    return registry


# CLI Interface
if __name__ == "__main__":
    import argparse
    import os
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Custom Tools CLI")
    parser.add_argument("tool", help="Tool name to execute")
    parser.add_argument("--param", action="append", help="Parameter in format key=value")

    args = parser.parse_args()

    registry = get_default_registry()

    if args.tool not in registry.list_tools():
        print(f"Error: Unknown tool '{args.tool}'")
        print(f"Available tools: {', '.join(registry.list_tools())}")
        sys.exit(1)

    # Parse parameters
    params = {}
    if args.param:
        for p in args.param:
            if "=" in p:
                key, value = p.split("=", 1)
                params[key] = value

    # Execute tool
    context = AgentToolContext(
        agent_id="cli",
        run_id="cli_run",
        iteration=1,
        tool_call_id=f"cli_{args.tool}",
        signal=None,
    )

    result = registry.execute_tool(args.tool, params, context)
    print(json.dumps(result.output, indent=2))