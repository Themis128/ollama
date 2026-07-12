#!/usr/bin/env python3
"""
Agentic CI Runner - Invokes DeepAgents + Ollama for CI operations.

This script bridges GitHub Actions with the agent infrastructure.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.cline_adapter import ClineAdapter
from integrations.agent_storm import AgentStorm, AgentStormConfig
from integrations.orchestrator_agent import Orchestrator, OrchestratorConfig
from integrations.debug_agent import DebugAgent, DebugConfig
from integrations.tdd_agent import TDDAgent, TDDConfig


def main():
    """Main entry point for agentic CI operations."""
    
    print("=" * 60)
    print("AGENTIC CI RUNNER")
    print("=" * 60)
    
    # Initialize agents
    storm = AgentStorm(AgentStormConfig())
    orchestrator = Orchestrator(OrchestratorConfig())
    
    # Run Agent Storm for infrastructure validation
    print("\n[1/3] Running Agent Storm validation...")
    result = storm.storm_with_roles(
        task="Validate ollama infrastructure code quality",
        prompt="Analyze the integrations/* and scripts/* for code quality, patterns, and best practices",
        roles=["architect", "security", "testing"]
    )
    
    # Run Orchestrator in auto mode
    print("\n[2/3] Running Orchestrator auto mode...")
    orch_result = orchestrator.execute(
        task="Verify deployment readiness of ollama infrastructure",
        mode="auto"
    )
    
    # Summary
    print("\n[3/3] Agentic CI Summary")
    print("-" * 40)
    print(f"✓ Agent Storm: {result['num_agents']} agents completed")
    print(f"✓ Orchestrator: {orch_result['mode']} mode validated")
    print("\nAgentic CI validation complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
