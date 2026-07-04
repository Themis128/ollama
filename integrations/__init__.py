"""
DeepAgents + Ollama Integration Package
========================================

Provides comprehensive integration between DeepAgents SDK and Ollama for
robust coding agents with production-ready capabilities.

Modules:
    - deepagents_ollama.py: Basic DeepAgents + Ollama integration
    - cloudless_gr_integration.py: cloudless.gr project integration
    - tdd_agent.py: Test-Driven Development with self-correction
    - terminal_agent.py: Terminal command execution
    - sandbox_agent.py: Isolated execution with security
    - orchestrator_agent.py: Multi-agent orchestration
    - web_agent.py: Internet communication and data fetching
    - debug_agent.py: Log analysis and self-fixing
    - agent_storm.py: Parallel multi-agent execution

Usage:
    from integrations.deepagents_ollama import create_ollama_agent
    from integrations.cloudless_gr_integration import create_cloudless_agent
    from integrations.cloudless_gr_integration import create_cloudflare_agent
    from integrations.tdd_agent import TDDAgent
    from integrations.agent_storm import AgentStorm
    
    # Basic Ollama agent
    agent = create_ollama_agent(model="qwen2.5-coder")
    
    # Cloudflare skills/MCP over Ollama
    agent = create_cloudflare_agent(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
        project_path="/path/to/project",
    )
    
    # Cloudless.gr agent with all features
    agent = create_cloudless_agent(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
    )
    
    # TDD agent for test-driven development
    tdd = TDDAgent(model="qwen2.5-coder")
    result = tdd.run_tdd("Create auth API", "test.ts", "api.ts")
    
    # Agent Storm for parallel execution
    storm = AgentStorm()
    result = storm.storm(task="Build user management", prompt="...")
"""

from typing import NoReturn

# Try to import deepagents modules, fall back to alternatives if not available
try:
    from .deepagents_ollama import create_ollama_agent
except (ImportError, ModuleNotFoundError):
    # Create fallback if deepagents is not installed
    def create_ollama_agent(*args, **kwargs) -> NoReturn:
        raise ImportError(
            "deepagents package is not installed. "
            "Install with: pip install deepagents"
        )

try:
    from .cloudless_gr_integration import create_cloudless_agent
    from .cloudless_gr_integration import create_cloudflare_agent
    from .cloudless_gr_integration import get_cloudflare_skills
    from .cloudless_gr_integration import get_cloudflare_mcp_servers
    from .cloudless_gr_integration import write_cloudflare_mcp_config
except (ImportError, ModuleNotFoundError):
    # Create fallback if deepagents is not installed
    def create_cloudless_agent(*args, **kwargs) -> NoReturn:
        raise ImportError(
            "deepagents package is not installed. "
            "Install with: pip install deepagents"
        )

    def create_cloudflare_agent(*args, **kwargs) -> NoReturn:
        raise ImportError(
            "deepagents package is not installed. "
            "Install with: pip install deepagents"
        )

    def get_cloudflare_skills(*args, **kwargs) -> NoReturn:
        raise ImportError(
            "deepagents package is not installed. "
            "Install with: pip install deepagents"
        )

    def get_cloudflare_mcp_servers(*args, **kwargs) -> NoReturn:
        raise ImportError(
            "deepagents package is not installed. "
            "Install with: pip install deepagents"
        )

    def write_cloudflare_mcp_config(*args, **kwargs) -> NoReturn:
        raise ImportError(
            "deepagents package is not installed. "
            "Install with: pip install deepagents"
        )

from .tdd_agent import TDDAgent
from .terminal_agent import TerminalAgent
from .sandbox_agent import SandboxAgent
from .orchestrator_agent import Orchestrator
from .web_agent import WebAgent
from .debug_agent import DebugAgent
from .agent_storm import AgentStorm, AgentRole

__all__ = [
    "create_ollama_agent",
    "create_cloudless_agent",
    "get_cloudflare_skills",
    "get_cloudflare_mcp_servers",
    "write_cloudflare_mcp_config",
    "TDDAgent",
    "TerminalAgent",
    "SandboxAgent",
    "Orchestrator",
    "WebAgent",
    "DebugAgent",
    "AgentStorm",
    "AgentRole",
]