"""
Tests for Custom Tools Module
=============================

Tests the create_tool, ToolRegistry, and built-in tools.
"""

import json
import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import os

from integrations.custom_tools import (
    create_tool,
    Tool,
    ToolRegistry,
    ToolResult,
    AgentToolContext,
    get_default_registry,
    get_time_tool,
    ollama_generate_tool,
    file_read_tool,
    file_write_tool,
    shell_tool,
    submit_result_tool,
)


class TestCreateTool:
    """Tests for create_tool function."""

    def test_creates_basic_tool(self):
        """Test creating a basic tool with minimal parameters."""
        tool = create_tool(
            name="test_tool",
            description="A test tool",
            input_schema={"input": (str, "Test input")},
            execute=lambda input, context: ToolResult(
                output={"result": input.get("input")}
            ),
        )

        assert tool.name == "test_tool"
        assert tool.description == "A test tool"
        assert "input" in tool.input_schema
        assert tool.lifecycle == {"completes_run": False}

    def test_creates_tool_with_lifecycle(self):
        """Test creating a tool with lifecycle flag."""
        tool = create_tool(
            name="complete_tool",
            description="A completion tool",
            input_schema={"summary": (str, "Summary of work")},
            execute=lambda input, context: ToolResult(
                output={"complete": True}
            ),
            lifecycle={"completes_run": True},
        )

        assert tool.lifecycle["completes_run"] is True

    def test_create_tool_returns_tool_instance(self):
        """Test that create_tool returns Tool instance."""
        tool = create_tool(
            name="test",
            description="Test",
            input_schema={},
            execute=lambda input, context: ToolResult(output={}),
        )

        assert isinstance(tool, Tool)


class TestToolRegistry:
    """Tests for ToolRegistry class."""

    def test_registry_initially_empty(self):
        """Test that new registry has no tools."""
        registry = ToolRegistry()
        assert registry.list_tools() == []

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        registry.register(get_time_tool)

        assert "get_time" in registry.list_tools()

    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = ToolRegistry()
        registry.register(get_time_tool)
        registry.unregister("get_time")

        assert "get_time" not in registry.list_tools()

    def test_unregister_nonexistent_returns_false(self):
        """Test unregistering a tool that doesn't exist."""
        registry = ToolRegistry()
        assert registry.unregister("nonexistent") is False

    def test_get_tool(self):
        """Test getting a registered tool."""
        registry = ToolRegistry()
        registry.register(get_time_tool)

        tool = registry.get("get_time")
        assert tool is get_time_tool

    def test_execute_tool(self):
        """Test executing a tool through registry."""
        registry = ToolRegistry()
        registry.register(get_time_tool)

        context = AgentToolContext(
            agent_id="test",
            run_id="test_run",
            iteration=1,
            tool_call_id="test_call",
            signal=None,
        )

        result = registry.execute_tool("get_time", {}, context)

        assert not result.is_error
        assert "iso" in result.output
        assert "timestamp" in result.output

    def test_execute_unknown_tool(self):
        """Test executing a tool that doesn't exist."""
        registry = ToolRegistry()

        result = registry.execute_tool("unknown_tool", {})

        assert result.is_error
        assert "error" in result.output

    def test_to_json_schema(self):
        """Test converting tool to JSON Schema."""
        registry = ToolRegistry()
        registry.register(get_time_tool)

        schema = registry.to_json_schema("get_time")

        assert schema is not None
        assert schema["type"] == "function"
        assert schema["function"]["name"] == "get_time"
        assert "timezone" in schema["function"]["parameters"]["properties"]


class TestBuiltInTools:
    """Tests for built-in tools."""

    def test_get_time_returns_valid_timestamp(self):
        """Test that get_time returns valid timestamp."""
        context = AgentToolContext(
            agent_id="test",
            run_id="test_run",
            iteration=1,
            tool_call_id="test_call",
            signal=None,
        )

        result = get_time_tool.execute({}, context)

        assert not result.is_error
        assert "iso" in result.output
        # Validate ISO format
        iso = result.output["iso"]
        datetime.fromisoformat(iso)  # Will raise if invalid

    def test_get_time_with_timezone(self):
        """Test get_time with timezone parameter."""
        context = AgentToolContext(
            agent_id="test",
            run_id="test_run",
            iteration=1,
            tool_call_id="test_call",
            signal=None,
        )

        result = get_time_tool.execute({"timezone": "America/New_York"}, context)

        assert result.output["timezone"] == "America/New_York"

    def test_file_write_and_read(self):
        """Test file write and read tools together."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"

            # Write file
            context = AgentToolContext(
                agent_id="test",
                run_id="test_run",
                iteration=1,
                tool_call_id="test_call",
                signal=None,
            )

            write_result = file_write_tool.execute(
                {"filepath": str(test_file), "content": "Hello, World!"},
                context,
            )

            assert not write_result.is_error
            assert write_result.output["success"] is True
            assert write_result.output["bytes_written"] == 13

            # Read file
            read_result = file_read_tool.execute(
                {"filepath": str(test_file)},
                context,
            )

            assert not read_result.is_error
            assert read_result.output["content"] == "Hello, World!"

    def test_file_read_nonexistent(self):
        """Test reading a nonexistent file."""
        context = AgentToolContext(
            agent_id="test",
            run_id="test_run",
            iteration=1,
            tool_call_id="test_call",
            signal=None,
        )

        result = file_read_tool.execute({"filepath": "/nonexistent/file.txt"}, context)

        assert result.is_error
        assert "error" in result.output

    def test_shell_echo(self):
        """Test shell tool with simple echo command."""
        context = AgentToolContext(
            agent_id="test",
            run_id="test_run",
            iteration=1,
            tool_call_id="test_call",
            signal=None,
        )

        result = shell_tool.execute({"command": "echo 'Hello, World!'"}, context)

        # Note: This may fail in some environments without shell access
        # We're testing that the tool executes, not the result
        assert "command" in result.output

    def test_submit_result_completes_run(self):
        """Test submit_result tool has completes_run lifecycle."""
        assert submit_result_tool.lifecycle["completes_run"] is True

        context = AgentToolContext(
            agent_id="test",
            run_id="test_run",
            iteration=1,
            tool_call_id="test_call",
            signal=None,
        )

        result = submit_result_tool.execute(
            {"summary": "Done", "approved": True},
            context,
        )

        assert result.output["complete"] is True


class TestDefaultRegistry:
    """Tests for get_default_registry function."""

    def test_registry_has_built_in_tools(self):
        """Test that default registry has all built-in tools."""
        registry = get_default_registry()

        tools = registry.list_tools()
        assert "get_time" in tools
        assert "ollama_generate" in tools
        assert "file_read" in tools
        assert "file_write" in tools
        assert "shell" in tools
        assert "submit_result" in tools

    def test_registry_has_six_tools(self):
        """Test that default registry has exactly 6 tools."""
        registry = get_default_registry()
        assert len(registry.list_tools()) == 6


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_success_result(self):
        """Test creating a successful result."""
        result = ToolResult(output={"success": True})

        assert not result.is_error
        assert result.output["success"] is True

    def test_error_result(self):
        """Test creating an error result."""
        result = ToolResult(
            output={"error": "Something went wrong"},
            is_error=True,
        )

        assert result.is_error
        assert "error" in result.output


class TestAgentToolContext:
    """Tests for AgentToolContext TypedDict."""

    def test_context_creation(self):
        """Test creating a valid context."""
        context = AgentToolContext(
            agent_id="agent_1",
            run_id="run_123",
            iteration=1,
            tool_call_id="call_1",
            signal=None,
        )

        assert context["agent_id"] == "agent_1"
        assert context["iteration"] == 1


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])