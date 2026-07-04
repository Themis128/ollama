"""Tests for the agent terminal helper."""

import os
import subprocess
import sys


def test_ollama_agent_terminal_help():
    """Test that terminal helper accepts --help."""
    result = subprocess.run(
        [sys.executable, "scripts/ollama-agent-terminal.py", "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, "Terminal helper should exit with 0"
    assert "usage" in result.stdout.lower(), "Should contain usage info"


def test_ollama_agent_terminal_simple_prompt():
    """Test terminal helper with a simple prompt."""
    result = subprocess.run(
        [sys.executable, "scripts/ollama-agent-terminal.py", "--model", "qwen2.5-coder", "Hello"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Should succeed: {result.stderr[:200]}"


def test_ollama_agent_terminal_python_code():
    """Test terminal helper with Python code generation."""
    result = subprocess.run(
        [sys.executable, "scripts/ollama-agent-terminal.py", "--model", "qwen2.5-coder", 
         "Write a Python function to calculate factorial"],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Should succeed: {result.stderr[:200]}"
    assert "def factorial" in result.stdout, "Should generate factorial function"
