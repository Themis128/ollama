"""
DeepAgents + Ollama Integration for cloudless.gr
===============================================

This module integrates DeepAgents with Ollama using the cloudless.gr project's:
- 8 custom skills (code-review, database, deploy, etc.)
- 4 specialized subagents (backend-dev, frontend-dev, devops, general-purpose)

Usage:
    from integrations.cloudless_gr_integration import create_cloudless_agent

    agent = create_cloudless_agent(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
    )

    # Use with skills
    result = agent.invoke({
        "messages": "Review the authentication flow",
        "skill": "code-review"
    })
"""

import os
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

# DeepAgents imports
from deepagents import create_deep_agent

# LangChain Ollama integration
from langchain_ollama import ChatOllama


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class CloudlessConfig:
    """Configuration for cloudless.gr DeepAgents integration."""
    base_url: str = "http://localhost:11434"
    model: str = "qwen2.5-coder"
    project_path: str = ""
    temperature: float = 0.1
    max_tokens: int = 4096
    top_p: float = 0.95
    streaming: bool = True
    timeout: int = 120

    def __post_init__(self):
        if not self.project_path:
            self.project_path = os.environ.get(
                "PROJECT_PATH",
                os.path.join(os.getcwd(), "cloudless.gr"),
            )


DEFAULT_CONFIG = CloudlessConfig()


# =============================================================================
# Skills Configuration
# =============================================================================

def get_cloudless_skills() -> List[str]:
    """Get list of available skills from cloudless.gr."""
    skills_dir = os.environ.get(
        "CLOUDLESS_GR_SKILLS_DIR",
        os.path.join(DEFAULT_CONFIG.project_path, ".deepagents", "skills"),
    )
    if os.path.exists(skills_dir):
        return [d for d in os.listdir(skills_dir) if os.path.isdir(os.path.join(skills_dir, d))]
    return []


def get_cloudflare_skills(skills_root: Optional[str] = None) -> List[str]:
    """
    Get list of available Cloudflare skills from the cloned skills repo.

    Use `scripts/setup-cloudflare-skills.sh` first to populate this directory.
    """
    if skills_root is None:
        skills_root = os.path.join(os.getcwd(), ".deepagents", "skills", "cloudflare")
    if os.path.exists(skills_root):
        return [d for d in os.listdir(skills_root) if os.path.isdir(os.path.join(skills_root, d))]
    return []


# =============================================================================
# Agent Creation
# =============================================================================

def create_cloudless_agent(
    model: str = "qwen2.5-coder",
    base_url: str = "http://localhost:11434",
    project_path: str = "/home/tbaltzakis/cloudless.gr",
    temperature: float = 0.1,
    max_tokens: int = 4096,
    skills: Optional[List[str]] = None,
) -> Any:
    """
    Create a DeepAgent for cloudless.gr with skills.

    Args:
        model: Ollama model name
        base_url: Ollama server URL
        project_path: Path to cloudless.gr project
        temperature: Generation temperature
        max_tokens: Maximum output tokens
        skills: List of skill names to enable

    Returns:
        Configured DeepAgent instance

    Example:
        agent = create_cloudless_agent(
            model="qwen2.5-coder",
            base_url="http://localhost:11434",
        )

        result = agent.invoke({
            "messages": "Review the authentication flow",
            "skill": "code-review"
        })
    """
    # Load skills from project if not provided
    if skills is None:
        skills = get_cloudless_skills()

    # Default coding-focused system prompt with cloudless.gr context
    default_coding_prompt = f"""You are an expert software developer and coding assistant for cloudless.gr.

Project: cloudless.gr
Path: {project_path}
Framework: Next.js 16 + TypeScript + Tailwind CSS
Database: DynamoDB (6 tables including sessions, transactions, user profiles)
Auth: AWS Cognito + next-auth v5
Deployment: AWS Lambda@Edge + K3s failover
Monitoring: Prometheus + Grafana + Loki + Sentry

## Your Capabilities:

### Skills Available:
{chr(10).join('  - ' + skill for skill in skills) if skills else '  None configured'}

## Project Guidelines:

1. Always use TypeScript with strict mode
2. Follow the existing code patterns in {project_path}/src
3. Use Zod for validation in API routes
4. Write tests for new features (Vitest + Playwright)
5. Update translations in src/locales/ for i18n
6. Use Sentry for error tracking
7. Check DynamoDB tables for data access patterns

When coding:
1. Understand the requirements fully before writing code
2. Use type hints and documentation strings
3. Handle errors gracefully
4. Write tests for your code
5. Consider edge cases
6. Follow the existing project structure

You have access to file operations, shell commands, and MCP servers to accomplish tasks.
Always explain your approach before implementing."""

    # Create the model
    llm_model = ChatOllama(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        base_url=base_url,
    )

    # Create the agent with skills
    agent = create_deep_agent(
        model=llm_model,
        system_prompt=default_coding_prompt,
        skills=skills,
    )

    print(f"[cloudless.gr Agent] Created agent with Ollama backend: {base_url}")
    print(f"[cloudless.gr Agent] Model: {model}")
    print(f"[cloudless.gr Agent] Project: {project_path}")
    print(f"[cloudless.gr Agent] Skills: {len(skills)}")

    return agent

# =============================================================================
# Utility Functions
# =============================================================================

def list_mcp_servers() -> List[str]:
    """List all available MCP servers in cloudless.gr."""
    mcp_path = "/home/tbaltzakis/cloudless.gr/.deepagents/.mcp.json"
    if os.path.exists(mcp_path):
        with open(mcp_path) as f:
            config = json.load(f)
        return list(config.get("mcpServers", {}).keys())
    return []


def get_cloudflare_mcp_servers() -> Dict[str, Dict[str, str]]:
    """
    Return the standard Cloudflare MCP server config block for agent configs.

    These values mirror the public servers documented in:
    https://github.com/cloudflare/mcp-server-cloudflare
    """
    return {
        "cloudflare": {"url": "https://mcp.cloudflare.com/mcp"},
        "cloudflare-docs": {"url": "https://docs.mcp.cloudflare.com/mcp"},
        "cloudflare-bindings": {"url": "https://bindings.mcp.cloudflare.com/mcp"},
        "cloudflare-builds": {"url": "https://builds.mcp.cloudflare.com/mcp"},
        "cloudflare-observability": {"url": "https://observability.mcp.cloudflare.com/mcp"},
        "cloudflare-containers": {"url": "https://containers.mcp.cloudflare.com/mcp"},
        "cloudflare-browser": {"url": "https://browser.mcp.cloudflare.com/mcp"},
        "cloudflare-logpush": {"url": "https://logs.mcp.cloudflare.com/mcp"},
        "cloudflare-ai-gateway": {"url": "https://ai-gateway.mcp.cloudflare.com/mcp"},
        "cloudflare-auditlogs": {"url": "https://auditlogs.mcp.cloudflare.com/mcp"},
        "cloudflare-dns-analytics": {"url": "https://dns-analytics.mcp.cloudflare.com/mcp"},
        "cloudflare-dex": {"url": "https://dex.mcp.cloudflare.com/mcp"},
        "cloudflare-one-casb": {"url": "https://cloudflare-one-casb.mcp.cloudflare.com/mcp"},
    }


def write_cloudflare_mcp_config(
    path: str = ".deepagents/.mcp.json",
) -> Dict[str, Any]:
    """
    Write a `.deepagents/.mcp.json` file containing Cloudflare MCP servers.

    Returns the written config dict.
    """
    config = {"mcpServers": get_cloudflare_mcp_servers()}
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(config, indent=2) + "\n")
    return config


def create_cloudflare_agent(
    model: str = "qwen2.5-coder",
    base_url: str = "http://localhost:11434",
    project_path: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 4096,
    enable_cloudflare_mcp: bool = True,
    mcp_config_path: str = ".deepagents/.mcp.json",
    skills: Optional[List[str]] = None,
) -> Any:
    """
    Create an Ollama-backed DeepAgent wired for Cloudflare skills/MCP usage.

    This writes Cloudflare MCP server config to `mcp_config_path` and loads
    Cloudflare skills from `.deepagents/skills/cloudflare` if available.

    Args:
        model: Ollama model name
        base_url: Ollama server URL
        project_path: Target project path for context
        temperature: Generation temperature
        max_tokens: Maximum output tokens
        enable_cloudflare_mcp: Whether to write Cloudflare MCP config
        mcp_config_path: Where to write `.deepagents/.mcp.json`
        skills: Optional explicit skills list

    Returns:
        Configured DeepAgent instance using Ollama + optional Cloudflare context
    """
    if project_path is None:
        project_path = os.environ.get("PROJECT_PATH", os.getcwd())

    if skills is None:
        cloudless_skills = get_cloudless_skills()
        cloudflare_skills = get_cloudflare_skills()
        combined_skills = list(dict.fromkeys(cloudless_skills + cloudflare_skills))
        skills = combined_skills

    if enable_cloudflare_mcp:
        write_cloudflare_mcp_config(mcp_config_path)

    system_prompt = f"""You are an expert software assistant operating with local Ollama inference.

Project: {project_path}
Model: {model}
Backend: Ollama @ {base_url}

## Context
- Use the target project conventions in `{project_path}`.
- Use Cloudflare-related skills from `.deepagents/skills/cloudflare/` when relevant.
- If `.deepagents/.mcp.json` exists, assume those MCP servers are available for tool use.

## Skills Available
{chr(10).join('  - ' + skill for skill in skills) if skills else '  None configured'}

## Guidelines
1. Prefer minimal, idiomatic changes.
2. Use available skills/MCP context first.
3. If a task needs Cloudflare APIs or docs, use the available Cloudflare skills or MCP servers.
4. Explain non-obvious choices briefly.
"""

    llm_model = ChatOllama(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        base_url=base_url,
    )

    agent = create_deep_agent(
        model=llm_model,
        system_prompt=system_prompt,
        skills=skills,
    )

    print(f"[Cloudflare Agent] Created Ollama-backed agent: {base_url}")
    print(f"[Cloudflare Agent] Model: {model}")
    print(f"[Cloudflare Agent] Project: {project_path}")
    print(f"[Cloudflare Agent] Skills: {len(skills)}")
    print(f"[Cloudflare Agent] MCP config: {'enabled' if enable_cloudflare_mcp else 'disabled'}")

    return agent


def show_project_info():
    """Display cloudless.gr project information."""
    print("=" * 60)
    print("CLOUDLESS.GR PROJECT INFO")
    print("=" * 60)
    print()
    print("Project Path:", DEFAULT_CONFIG.project_path)
    print()
    print("MCP Servers:")
    for server in list_mcp_servers():
        print(f"  - {server}")
    print()
    print("Skills:")
    for skill in get_cloudless_skills():
        print(f"  - {skill}")


# =============================================================================
# CLI Usage
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DeepAgents + Ollama + cloudless.gr Integration")
    print("=" * 60)
    print()

    # Show project info
    show_project_info()

    print()
    print("=" * 60)
    print("Usage Example:")
    print("=" * 60)
    print("""
from integrations.cloudless_gr_integration import create_cloudless_agent

# Create agent with cloudless.gr skills
agent = create_cloudless_agent(
    model="qwen2.5-coder",
    base_url="http://localhost:11434",
)

# Use with skills
result = agent.invoke({
    "messages": "Review the authentication flow",
    "skill": "code-review"
})

# Use with a query
result = agent.invoke({
    "messages": "Create a new API endpoint for user feedback"
})
""")