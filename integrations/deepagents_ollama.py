"""
DeepAgents + Ollama Integration Module
=======================================

This module provides a robust bridge between DeepAgents SDK and Ollama engine
for building powerful coding agents with local inference.

Based on official LangChain documentation: https://docs.langchain.com/oss/python/integrations/chat/ollama

Features:
- Provider registration for Ollama
- Native tool calling support via ChatOllama
- Streaming support
- Multiple model support (qwen2.5-coder, llama3.1, mistral, etc.)
- Session management

Usage:
    from integrations.deepagents_ollama import create_ollama_agent

    # Create agent with Ollama backend
    agent = create_ollama_agent(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
    )

    result = agent.invoke({"messages": "Write a Python function to calculate fibonacci"})
"""

import os
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# DeepAgents imports
from deepagents import create_deep_agent, ProviderProfile, register_provider_profile

# LangChain Ollama integration (official recommended approach)
# pip install -qU langchain-ollama
from langchain_ollama import ChatOllama


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class OllamaConfig:
    """Configuration for Ollama DeepAgents integration."""
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder"
    temperature: float = 0.1  # Lower for coding tasks
    max_tokens: int = 4096
    top_p: float = 0.95
    streaming: bool = True
    timeout: int = 120
    api_key: str = "dummy"  # Not required for local Ollama


# Default config instance
DEFAULT_CONFIG = OllamaConfig()


# =============================================================================
# Provider Registration
# =============================================================================

def register_ollama_provider(
    base_url: str = "http://localhost:11434",
    api_key: str = "dummy",
    model: str = "qwen2.5-coder",
) -> None:
    """
    Register Ollama as a DeepAgents provider.

    This enables using provider:model strings like:
    - ollama:qwen2.5-coder
    - ollama:llama3.1

    Args:
        base_url: Ollama server URL
        api_key: API key (dummy works for local Ollama)
        model: Model identifier
    """
    # Register provider-wide profile
    register_provider_profile(
        "ollama",
        ProviderProfile(
            init_kwargs={
                "base_url": base_url,
                "api_key": api_key,
                "temperature": 0.1,  # Lower temperature for precise coding
                "max_tokens": 4096,
                "timeout": 120,
            }
        ),
    )

    # Register model-specific profile
    register_provider_profile(
        f"ollama:{model}",
        ProviderProfile(
            init_kwargs={
                "base_url": base_url,
                "api_key": api_key,
                "temperature": 0.1,
                "max_tokens": 4096,
                "top_p": 0.95,
                "timeout": 120,
            }
        ),
    )

    print(f"[Ollama Integration] Registered provider: ollama -> {base_url}")
    print(f"[Ollama Integration] Registered model: ollama:{model}")


# =============================================================================
# Model Initialization
# =============================================================================

def get_ollama_model(
    config: Optional[OllamaConfig] = None,
) -> ChatOllama:
    """
    Get a configured ChatOllama instance.

    Uses the official langchain_ollama.ChatOllama class.

    Args:
        config: OllamaConfig instance (uses defaults if None)

    Returns:
        ChatOllama instance configured for Ollama
    """
    if config is None:
        config = DEFAULT_CONFIG

    # Use ChatOllama directly - connects to localhost:11434 by default
    model = ChatOllama(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        top_p=config.top_p,
        base_url=config.base_url,  # Override default localhost:11434 if needed
        streaming=config.streaming,
        timeout=config.timeout,
    )

    return model


# =============================================================================
# Agent Creation
# =============================================================================

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
) -> Any:
    """
    Create a DeepAgent powered by Ollama.

    This is the main entry point for creating coding agents with Ollama.

    Args:
        model: Ollama model name (qwen2.5-coder, llama3.1, mistral, etc.)
        base_url: Ollama server URL
        api_key: API key (dummy for local Ollama)
        system_prompt: Custom system prompt (uses coding default if None)
        tools: Optional list of custom tools
        middleware: Optional middleware list
        temperature: Generation temperature (lower = more precise)
        max_tokens: Maximum output tokens
        timeout: Request timeout in seconds

    Returns:
        Configured DeepAgent instance

    Example:
        agent = create_ollama_agent(
            model="qwen2.5-coder",
            base_url="http://localhost:11434",
            system_prompt="You are an expert Python developer...",
        )

        result = agent.invoke({
            "messages": "Create a REST API with FastAPI"
        })
    """
    # Register Ollama provider
    register_ollama_provider(
        base_url=base_url,
        api_key=api_key,
        model=model,
    )

    # Default coding-focused system prompt
    default_coding_prompt = """You are an expert software developer and coding assistant.
You excel at:
- Writing clean, maintainable code
- Designing robust APIs
- Debugging complex issues
- Writing comprehensive tests
- Following best practices

When coding:
1. Understand the requirements fully before writing code
2. Use type hints and documentation strings
3. Handle errors gracefully
4. Write tests for your code
5. Consider edge cases

You have access to file operations, shell commands, and can use tools to accomplish tasks.
Always explain your approach before implementing."""

    final_prompt = system_prompt or default_coding_prompt

    # Get configured model
    config = OllamaConfig(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )
    llm_model = get_ollama_model(config)

    # Create the agent
    agent = create_deep_agent(
        model=llm_model,
        system_prompt=final_prompt,
        tools=tools or [],
        middleware=middleware or [],
    )

    print(f"[Ollama Agent] Created agent with Ollama backend: {base_url}")
    print(f"[Ollama Agent] Model: {model}")
    print(f"[Ollama Agent] Temperature: {temperature}")

    return agent


# =============================================================================
# Quick Test Function
# =============================================================================

async def test_ollama_connection(
    base_url: str = "http://localhost:11434",
    api_key: str = "dummy",
    model: str = "qwen2.5-coder",
) -> bool:
    """
    Test the Ollama connection and model availability.

    Args:
        base_url: Ollama server URL
        api_key: API key
        model: Model name

    Returns:
        True if connection successful, raises exception otherwise
    """
    import httpx

    print(f"[Test] Connecting to Ollama at {base_url}...")

    # Test health endpoint
    try:
        async with httpx.AsyncClient() as client:
            # Check models endpoint
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            models_data = response.json()
            models = [m["name"] for m in models_data.get("models", [])]
            print(f"[Test] Available models: {models}")

            if model in models:
                print(f"[Test] ✓ Model '{model}' is available")
            else:
                print(f"[Test] ⚠ Model '{model}' not found in available models")
                print(f"[Test] Available: {models}")

    except Exception as e:
        print(f"[Test] ✗ Connection failed: {e}")
        raise

    # Test basic generation
    try:
        test_model = get_ollama_model(
            OllamaConfig(base_url=base_url, api_key=api_key, model=model)
        )

        # Simple test invocation
        from langchain_core.messages import HumanMessage

        messages = [HumanMessage(content="Write 'Hello, Ollama!' in Python")]
        response = await test_model.ainvoke(messages)

        print(f"[Test] ✓ Generation test passed")
        print(f"[Test] Response: {response.content[:100]}...")

    except Exception as e:
        print(f"[Test] ✗ Generation test failed: {e}")
        raise

    print("[Test] ✓ All Ollama connection tests passed!")
    return True


# =============================================================================
# Utility Functions
# =============================================================================

def list_available_models(
    base_url: str = "http://localhost:11434",
) -> List[Dict[str, Any]]:
    """
    List all available models in Ollama.

    Args:
        base_url: Ollama server URL

    Returns:
        List of model information dictionaries
    """
    import httpx
    import json

    try:
        response = httpx.get(f"{base_url}/api/tags", timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("models", [])
    except Exception as e:
        print(f"[Error] Failed to list models: {e}")
        return []


def pull_model(
    model: str = "qwen2.5-coder",
    base_url: str = "http://localhost:11434",
) -> bool:
    """
    Pull a model from Ollama registry.

    Args:
        model: Model name to pull
        base_url: Ollama server URL

    Returns:
        True if successful
    """
    import subprocess

    try:
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[Error] Failed to pull model: {e}")
        return False


# =============================================================================
# CLI Usage
# =============================================================================

if __name__ == "__main__":
    import asyncio

    print("=" * 60)
    print("DeepAgents + Ollama Integration Test")
    print("=" * 60)

    # List available models
    print("\nAvailable Ollama models:")
    models = list_available_models()
    for m in models:
        print(f"  - {m.get('name', 'unknown')} ({m.get('size', 0) / (1024**3):.2f} GB)")

    # Run connection test
    try:
        asyncio.run(test_ollama_connection())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTo start Ollama, run:")
        print("  ollama serve")
        print("  # or")
        print("  docker run -d --gpus all -v ollama:/root/.ollama -p 11434:11434 ollama/ollama:latest")
        exit(1)

    print("\n" + "=" * 60)
    print("Usage Example:")
    print("=" * 60)
    print("""
from integrations.deepagents_ollama import create_ollama_agent

# Create agent
agent = create_ollama_agent(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
    system_prompt="You are a Python expert...",
)

# Use agent
result = agent.invoke({
    "messages": "Create a FastAPI endpoint for user authentication"
})
""")