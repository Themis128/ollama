"""
Multi-Agent Orchestrator Module
================================

Orchestrates multiple specialized agents (Architect, Code, Debug) with mode switching.
Implements the hybrid agentic workflow: plan in IDE, execute in sandbox, verify in CI.

Usage:
    from integrations.orchestrator_agent import Orchestrator
    
    orchestrator = Orchestrator(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
    )
    
    # Use specific mode
    result = orchestrator.execute(
        mode="architect",
        task="Design the user authentication system"
    )
    
    # Auto-switch modes for complex task
    result = orchestrator.execute(
        mode="auto",
        task="Implement user registration with email verification"
    )
"""

import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from langchain_ollama import ChatOllama  # type: ignore


class AgentMode(Enum):
    """Available agent modes."""
    ARCHITECT = "architect"
    CODE = "code"
    DEBUG = "debug"
    ORCHESTRATOR = "orchestrator"
    AUTO = "auto"


@dataclass
class OrchestratorConfig:
    """Configuration for orchestrator."""
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    max_modes: int = 5  # Max mode switches per task


class Orchestrator:
    """Multi-agent orchestrator with mode switching."""
    
    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()
        self.llm = ChatOllama(
            model=self.config.model,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
        )
        self.current_mode = AgentMode.CODE
        self.history: List[Dict[str, Any]] = []
        
        # Mode descriptions
        self.mode_prompts = {
            "architect": """You are an Architect Agent. Your role:
- Design system architecture and patterns
- Make high-level decisions
- Create technical specifications
- Review code quality and standards
- Plan multi-file implementations

Focus on the big picture, not implementation details.""",
            
            "code": """You are a Code Agent. Your role:
- Write implementation code
- Fix bugs in code
- Refactor existing code
- Add tests and documentation
- Follow existing patterns exactly

Focus on implementation, not design decisions.""",
            
            "debug": """You are a Debug Agent. Your role:
- Analyze error messages and logs
- Identify root causes of failures
- Suggest fixes for errors
- Run diagnostic commands
- Explain complex errors

Focus on understanding and fixing failures.""",
            
            "orchestrator": """You are an Orchestrator Agent. Your role:
- Switch between Architect, Code, and Debug modes
- Break complex tasks into subtasks
- Track task progress
- Coordinate between agents
- Ensure end-to-end completion""",
            
            "auto": """You are an autonomous agent. Automatically switch modes:
- Use ARCHITECT mode for planning and design
- Use CODE mode for implementation
- Use DEBUG mode for fixing failures
- Stay in the current mode unless switching is needed""",
        }
        
    def execute(
        self,
        task: str,
        mode: str = "auto",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute task using appropriate mode(s).
        
        Args:
            task: Task description
            mode: Agent mode (auto, architect, code, debug, orchestrator)
            context: Additional context for the task
            
        Returns:
            Result dictionary with output and metadata
        """
        # Convert mode string to enum
        try:
            mode_enum = AgentMode(mode.lower())
        except ValueError:
            mode_enum = AgentMode.AUTO
            
        # If AUTO mode, start with architect for complex tasks
        if mode_enum == AgentMode.AUTO:
            mode_enum = AgentMode.ARCHITECT
        
        current_mode = mode_enum
        
        # Prepare prompt
        system_prompt = self.mode_prompts[current_mode.value]
        
        full_prompt = f"""{system_prompt}

TASK: {task}

Current mode: {current_mode.value}

Please execute the task using this mode's responsibilities."""
        
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        # Execute
        response = self.llm.invoke(full_prompt)
        
        result = {
            "success": True,
            "mode": current_mode.value,
            "task": task,
            "output": response.content,
            "mode_switches": 0,
            "history": [],
        }
        
        # Handle AUTO mode switching
        if mode_enum == AgentMode.AUTO:
            result = self._auto_mode_execute(task, context)
        
        self.history.append(result)
        return result
    
    def _auto_mode_execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute with automatic mode switching."""
        result = {
            "success": False,
            "task": task,
            "stages": [],
            "final_output": "",
        }
        
        # Phase 1: Architect mode - plan
        print("[ARCHITECT] Planning...")
        plan = self._execute_with_mode(
            "architect",
            f"Create a detailed implementation plan for: {task}",
            context
        )
        result["stages"].append({
            "mode": "architect",
            "output": plan,
        })
        
        # Phase 2: Code mode - implement
        print("[CODE] Implementing...")
        implementation = self._execute_with_mode(
            "code",
            f"Implement the following plan:\n\n{plan}\n\nTask: {task}",
            context
        )
        result["stages"].append({
            "mode": "code",
            "output": implementation,
        })
        
        # Phase 3: Debug mode - verify and fix
        print("[DEBUG] Verifying...")
        verification = self._execute_with_mode(
            "debug",
            f"Verify the implementation and fix any issues:\n\n{implementation}\n\nTask: {task}",
            context
        )
        result["stages"].append({
            "mode": "debug",
            "output": verification,
        })
        
        # Final result
        result["success"] = True
        result["final_output"] = implementation
        result["total_stages"] = len(result["stages"])
        
        return result
    
    def _execute_with_mode(
        self,
        mode: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Execute prompt with specific mode."""
        system_prompt = self.mode_prompts.get(mode, self.mode_prompts["code"])
        
        full_prompt = f"""{system_prompt}

{prompt}"""
        
        if context:
            full_prompt += f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        response = self.llm.invoke(full_prompt)
        content = response.content if isinstance(response.content, str) else ""
        return content
    
    def switch_mode(self, new_mode: str) -> bool:
        """Switch to a new agent mode."""
        try:
            self.current_mode = AgentMode(new_mode.lower())
            return True
        except ValueError:
            return False
    
    def get_mode_history(self) -> List[str]:
        """Get list of modes used in current session."""
        return [entry["mode"] for entry in self.history if entry.get("mode")]


# CLI Interface
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Orchestrator Agent")
    parser.add_argument("task", help="Task to execute")
    parser.add_argument("--mode", default="auto", choices=["auto", "architect", "code", "debug", "orchestrator"], help="Agent mode")
    parser.add_argument("--model", default="qwen2.5-coder", help="Model name")
    parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama URL")
    parser.add_argument("--context", help="Context JSON file")
    
    args = parser.parse_args()
    
    # Load context if provided
    context = None
    if args.context:
        with open(args.context) as f:
            context = json.load(f)
    
    orchestrator = Orchestrator(OrchestratorConfig(
        model=args.model,
        base_url=args.base_url,
    ))
    
    result = orchestrator.execute(
        task=args.task,
        mode=args.mode,
        context=context,
    )
    
    print(f"\n{'='*60}")
    print(f"RESULT (Mode: {result['mode']})")
    print(f"{'='*60}")
    print(result.get("output", result.get("final_output", "N/A")))
    print(f"\nMode switches: {result.get('mode_switches', 'N/A')}")