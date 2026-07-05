"""
Agent Storm Module
==================

Implements the Agent Storm pattern - a parallel multi-agent execution that:
1. Spawns specialized agents for different aspects of a task
2. Runs them in parallel to gather diverse perspectives
3. Combines results using a synthesizer agent
4. Optimizes for comprehensive, high-quality outputs

This pattern is inspired by "Agent Storming" - a technique for complex problem solving
using multiple specialized agents in parallel.

Usage:
    from integrations.agent_storm import AgentStorm
    
    storm = AgentStorm(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
        num_agents=4,
    )
    
    # Run agent storm
    result = storm.storm(
        task="Design a user authentication system",
        prompt="Create a comprehensive authentication solution",
    )
    
    # Use specific agent roles
    result = storm.storm_with_roles(
        task="Implement REST API for user management",
        roles=["architect", "backend", "security", "testing"],
    )
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from langchain_ollama import ChatOllama  # type: ignore


@dataclass
class AgentStormConfig:
    """Configuration for Agent Storm."""
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    num_agents: int = 4
    max_workers: int = 4  # Parallel execution workers
    synthesizer_model: str = "qwen2.5-coder"
    timeout: int = 300  # Total timeout in seconds


@dataclass
class AgentRole:
    """Definition of an agent role."""
    name: str
    system_prompt: str
    focus: str  # What this agent focuses on


# Pre-defined agent roles
DEFAULT_ROLES = [
    AgentRole(
        name="architect",
        system_prompt="""You are an Architect Agent. Your focus:
- System design and architecture
- High-level patterns and structure
- Technology stack selection
- Scalability and maintainability
- Trade-off analysis""",
        focus="system architecture and design patterns",
    ),
    AgentRole(
        name="backend",
        system_prompt="""You are a Backend Agent. Your focus:
- API design and implementation
- Database schemas and queries
- Business logic
- Authentication and authorization
- Performance optimization""",
        focus="backend implementation and data layer",
    ),
    AgentRole(
        name="security",
        system_prompt="""You are a Security Agent. Your focus:
- Security vulnerabilities and threats
- Authentication and authorization flows
- Input validation and sanitization
- Secure coding practices
- Compliance and best practices""",
        focus="security vulnerabilities and best practices",
    ),
    AgentRole(
        name="testing",
        system_prompt="""You are a Testing Agent. Your focus:
- Test coverage and quality
- Edge cases and error handling
- Unit, integration, and E2E tests
- Test strategy and architecture
- Test automation and CI/CD""",
        focus="testing strategy and coverage",
    ),
    AgentRole(
        name="frontend",
        system_prompt="""You are a Frontend Agent. Your focus:
- User interface design
- React components and hooks
- State management
- Accessibility and UX
- Responsive design""",
        focus="frontend implementation and UX",
    ),
    AgentRole(
        name="devops",
        system_prompt="""You are a DevOps Agent. Your focus:
- Infrastructure as code
- Deployment strategies
- CI/CD pipelines
- Monitoring and logging
- Infrastructure optimization""",
        focus="deployment and infrastructure",
    ),
]


class AgentStorm:
    """Agent Storm - parallel multi-agent execution pattern."""
    
    def __init__(self, config: Optional[AgentStormConfig] = None):
        self.config = config or AgentStormConfig()
        self.roles = DEFAULT_ROLES
        self.results: List[Dict[str, Any]] = []
        
    def storm(
        self,
        task: str,
        prompt: str,
        num_agents: Optional[int] = None,
        custom_roles: Optional[List[AgentRole]] = None,
    ) -> Dict[str, Any]:
        """
        Run Agent Storm - parallel execution of multiple agents.
        
        Args:
            task: Main task description
            prompt: Detailed prompt for agents
            num_agents: Number of agents to spawn
            custom_roles: Optional custom agent roles
            
        Returns:
            Combined results from all agents
        """
        start_time = datetime.now()
        
        # Determine number of agents
        actual_num_agents = num_agents or self.config.num_agents
        
        # Select roles (use custom or default)
        selected_roles = custom_roles or self.roles[:actual_num_agents]
        
        # Prepare prompts for each agent
        agent_prompts = []
        for role in selected_roles:
            agent_prompt = f"""{role.system_prompt}

TASK: {task}

YOUR FOCUS: {role.focus}

INSTRUCTIONS: {prompt}

Provide your comprehensive analysis, implementation, or solution focusing on your area of expertise."""
            agent_prompts.append({
                "role": role.name,
                "prompt": agent_prompt,
            })
        
        # Execute agents in parallel
        print(f"\n{'='*60}")
        print(f"AGENT STORM: Running {actual_num_agents} agents in parallel")
        print(f"{'='*60}\n")
        
        results = self._execute_parallel(agent_prompts)
        
        # Synthesize results
        synthesis = self._synthesize_results(task, results)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Store results
        self.results.append({
            "task": task,
            "num_agents": len(results),
            "duration": duration,
            "individual_results": results,
            "synthesis": synthesis,
        })
        
        return {
            "success": True,
            "task": task,
            "num_agents": len(results),
            "duration_seconds": duration,
            "individual_results": results,
            "synthesis": synthesis,
        }
    
    def storm_with_roles(
        self,
        task: str,
        prompt: str,
        roles: List[str],
    ) -> Dict[str, Any]:
        """
        Run Agent Storm with specific role names.
        
        Args:
            task: Main task description
            prompt: Detailed prompt for agents
            roles: List of role names (architect, backend, security, etc.)
            
        Returns:
            Combined results from specified roles
        """
        selected_roles = [r for r in self.roles if r.name.lower() in [role.lower() for role in roles]]
        
        if not selected_roles:
            return {"success": False, "error": "No valid roles found"}
        
        return self.storm(task, prompt, custom_roles=selected_roles)
    
    def _execute_parallel(self, prompts: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Execute agents in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_role = {
                executor.submit(self._execute_agent, p["role"], p["prompt"]): p["role"]
                for p in prompts
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_role):
                role = future_to_role[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"  ✓ {role}: Completed")
                except Exception as e:
                    results.append({
                        "role": role,
                        "success": False,
                        "error": str(e),
                    })
                    print(f"  ✗ {role}: Failed - {e}")
        
        return results
    
    def _execute_agent(self, role: str, prompt: str) -> Dict[str, Any]:
        """Execute a single agent."""
        llm = ChatOllama(
            model=self.config.model,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
        )
        
        response = llm.invoke(prompt)
        
        return {
            "role": role,
            "success": True,
            "output": response.content,
        }
    
    def _synthesize_results(
        self,
        task: str,
        results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Synthesize results from multiple agents using a synthesizer agent."""
        # Prepare synthesis prompt
        synthesis_prompt = f"""You are a synthesizer agent. Your task is to combine multiple agent responses into a coherent final answer.

MAIN TASK: {task}

INCOMING RESPONSES:
"""

        for i, result in enumerate(results, 1):
            status = "✓" if result.get("success") else "✗"
            synthesis_prompt += f"""
--- Response {i} ({result['role']}) [{status}] ---
{result.get('output', result.get('error', 'No output'))[:5000]}
--- End Response {i} ---
"""

        synthesis_prompt += """
SYNTHESIS TASK:
Combine these responses into a coherent, comprehensive answer. Prioritize:
1. Technical accuracy and consistency
2. Completeness of information
3. Actionable recommendations
4. Integration of different perspectives

Provide a well-structured synthesis that integrates all perspectives."""
        
        # Execute synthesizer
        synthesizer = ChatOllama(
            model=self.config.synthesizer_model,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
        )
        
        synthesis = synthesizer.invoke(synthesis_prompt)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "synthesis": synthesis.content,
            "input_count": len(results),
        }
    
    def parallel_tasks(
        self,
        task: str,
        subtasks: List[str],
    ) -> Dict[str, Any]:
        """
        Execute multiple subtasks in parallel using specialized agents.
        
        Args:
            task: Main task description
            subtasks: List of subtasks to execute in parallel
            
        Returns:
            Results from all subtasks
        """
        start_time = datetime.now()
        
        print(f"\n{'='*60}")
        print("AGENT STORM: Parallel Task Execution")
        print(f"{'='*60}\n")
        
        results = []
        for i, subtask in enumerate(subtasks, 1):
            print(f"[{i}/{len(subtasks)}] {subtask}")
            
            # Use different roles for different subtasks
            role_idx = (i - 1) % len(self.roles)
            role = self.roles[role_idx]
            
            agent_prompt = f"""{role.system_prompt}

MAIN TASK: {task}
SUBTASK: {subtask}

Focus on: {role.focus}

Provide your analysis or implementation."""
            
            result = self._execute_agent(role.name, agent_prompt)
            result["subtask"] = subtask
            results.append(result)
            
            if result.get("success"):
                print(f"  ✓ {role.name}: Completed")
            else:
                print(f"  ✗ {role.name}: Failed - {result.get('error', 'Unknown error')}")
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            "success": True,
            "task": task,
            "num_subtasks": len(subtasks),
            "duration_seconds": duration,
            "results": results,
        }
    
    def get_results(self) -> List[Dict[str, Any]]:
        """Get all storm results."""
        return self.results
    
    def clear_results(self) -> None:
        """Clear stored results."""
        self.results = []


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Storm")
    parser.add_argument("task", help="Main task description")
    parser.add_argument("--prompt", default="Create a comprehensive solution", help="Detailed prompt")
    parser.add_argument("--num-agents", type=int, default=4, help="Number of agents")
    parser.add_argument("--model", default="qwen2.5-coder", help="Model name")
    parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama URL")
    
    args = parser.parse_args()
    
    storm = AgentStorm(AgentStormConfig(
        model=args.model,
        base_url=args.base_url,
        num_agents=args.num_agents,
    ))
    
    result = storm.storm(
        task=args.task,
        prompt=args.prompt,
        num_agents=args.num_agents,
    )
    
    print(f"\n{'='*60}")
    print("AGENT STORM COMPLETE")
    print(f"{'='*60}")
    print(f"Task: {result['task']}")
    print(f"Agents: {result['num_agents']}")
    print(f"Duration: {result['duration_seconds']:.2f}s")
    print("\nSynthesis:")
    print(result['synthesis']['synthesis'][:2000])