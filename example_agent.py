"""
Example: DeepAgents + Ollama Agent Setup
======================================

This demonstrates how to use all available tools and skills in your app.
"""

import sys
sys.path.insert(0, '/home/tbaltzakis/ollama')

# =============================================================================
# Method 1: Using built-in custom tools
# =============================================================================
from integrations import get_default_registry, create_tool, ToolResult, AgentToolContext

# Get default tool registry
registry = get_default_registry()
print("Built-in tools:", registry.list_tools())

# Example: Use ollama_generate tool
result = registry.execute_tool("ollama_generate", {
    "prompt": "Write a hello world in Python",
    "model": "qwen2.5-coder"
})
print("\nOllama response:", result.output.get("response", "")[:100])

# =============================================================================
# Method 2: Create custom tools
# =============================================================================
def my_custom_action(input_dict, context):
    """Your custom business logic here."""
    return ToolResult(output={
        "processed": True,
        "input": input_dict,
        "agent_id": context.get("agent_id", "unknown")
    })

custom_tool = create_tool(
    name="my_custom_action",
    description="Your custom tool description for the LLM",
    input_schema={"message": (str, "Message to process")},
    execute=my_custom_action
)
registry.register(custom_tool)
print("\nRegistered custom tools:", registry.list_tools())

# =============================================================================
# Method 3: Use GitHub MCP tools directly
# =============================================================================
# Example: Search for a repo
# from mcp_client import use_mcp_tool  # Would use cz_VTX0mcp0 prefixed functions
# repo = await use_mcp_tool("cz_VTX0mcp0search_repositories", {"query": "your-search"})

# =============================================================================
# Method 4: Load specialized skills when needed
# =============================================================================
# For Azure, Cloudflare, etc. - call use_skill("skill-name") before using
# This activates the skill's specialized capabilities

print("\n✅ Integration ready! Use skills and tools as needed.")
print("Available skills: azure-*, cloudflare-*, playwright-cli, entra-*, appinsights-*")