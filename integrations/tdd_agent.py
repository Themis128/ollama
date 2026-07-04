"""
TDD (Test-Driven Development) Agent Module
===========================================

Implements the red-green-refactor cycle for autonomous coding:
- RED: Write failing test that captures expected behavior
- GREEN: Implement minimal code to make test pass
- REFACTOR: Clean up implementation while keeping tests green
- SELF-CORRECT: Agent reads failures and patches code automatically

Usage:
    from integrations.tdd_agent import TDDAgent
    
    agent = TDDAgent(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
        project_path="/home/tbaltzakis/cloudless.gr",
    )
    
    # Auto TDD loop
    result = agent.run_tdd(
        feature="Create a user authentication API endpoint",
        test_file="src/app/api/auth/route.test.ts",
        implementation_file="src/app/api/auth/route.ts",
    )
"""

import os
import re
import subprocess
import time
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from pathlib import Path

from langchain_ollama import ChatOllama


@dataclass
class TDDConfig:
    """Configuration for TDD agent."""
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    max_iterations: int = 10
    timeout: int = 60  # seconds per iteration


class TDDAgent:
    """TDD (Test-Driven Development) Agent with autonomous self-correction."""
    
    def __init__(self, config: Optional[TDDConfig] = None):
        self.config = config or TDDConfig()
        self.llm = ChatOllama(
            model=self.config.model,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
        )
        self.iteration_count = 0
        self.history: List[Dict[str, Any]] = []
        
    def run_tdd(
        self,
        feature: str,
        test_file: str,
        implementation_file: str,
        test_command: str = "pnpm test",
    ) -> Dict[str, Any]:
        """
        Run complete TDD loop for a feature.
        
        Args:
            feature: Description of the feature to implement
            test_file: Path to test file
            implementation_file: Path to implementation file
            test_command: Command to run tests
            
        Returns:
            Result dictionary with status and details
        """
        print(f"\n{'='*60}")
        print(f"TDD AGENT: Starting TDD loop for '{feature}'")
        print(f"{'='*60}\n")
        
        # Phase 1: RED - Write failing test
        print("[RED] Phase: Writing failing test...")
        test_code = self._write_failing_test(feature, test_file, implementation_file)
        
        # Write test file
        self._write_file(test_file, test_code)
        print(f"  ✓ Created test file: {test_file}")
        
        # Run test (expect failure)
        if not self._run_test(test_command):
            print("  ✓ Test failed as expected (RED phase complete)")
        else:
            print("  ⚠ Test passed unexpectedly - resetting...")
            self._reset_files(test_file, implementation_file)
        
        # Phase 2: GREEN - Implement minimal code
        print("\n[GREEN] Phase: Implementing minimal code...")
        implementation_code = self._write_implementation(feature, implementation_file, test_file)
        self._write_file(implementation_file, implementation_code)
        print(f"  ✓ Created implementation: {implementation_file}")
        
        # Run test (expect success)
        if self._run_test(test_command):
            print("  ✓ All tests passing (GREEN phase complete)")
        else:
            print("  ⚠ Test still failing - self-correcting...")
            # Phase 3: REFACTOR & SELF-CORRECT
            return self._self_correct(
                feature=feature,
                test_file=test_file,
                implementation_file=implementation_file,
                test_command=test_command,
            )
        
        return {
            "status": "success",
            "feature": feature,
            "test_file": test_file,
            "implementation_file": implementation_file,
            "iterations": self.iteration_count,
            "history": self.history,
        }
    
    def _write_failing_test(
        self,
        feature: str,
        test_file: str,
        implementation_file: str,
    ) -> str:
        """Write failing test that captures expected behavior."""
        prompt = f"""You are writing a failing test in a TDD cycle.

FEATURE: {feature}
TEST FILE: {test_file}
IMPLEMENTATION FILE: {implementation_file}

Write a comprehensive test file that:
1. Tests all edge cases for the feature
2. Fails initially (before implementation exists)
3. Uses proper TypeScript/JavaScript syntax
4. Includes proper imports and setup
5. Uses Vitest/Jest-style assertions

Do NOT implement the feature - only write the test.
Return ONLY the test code with no explanation."""
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def _write_implementation(
        self,
        feature: str,
        implementation_file: str,
        test_file: str,
    ) -> str:
        """Write minimal implementation to make tests pass."""
        prompt = f"""You are implementing minimal code in a TDD cycle.

FEATURE: {feature}
IMPLEMENTATION FILE: {implementation_file}
TEST FILE: {test_file}

Write the minimal implementation to make tests pass:
1. Implement ONLY what the tests require
2. Follow existing code patterns in the project
3. Use TypeScript with strict type hints
4. Add JSDoc comments for public functions
5. Handle edge cases mentioned in tests

Do NOT add extra functionality - implement only what's tested.
Return ONLY the implementation code with no explanation."""
        
        response = self.llm.invoke(prompt)
        return response.content
    
    def _self_correct(
        self,
        feature: str,
        test_file: str,
        implementation_file: str,
        test_command: str,
    ) -> Dict[str, Any]:
        """Self-correct until tests pass."""
        print(f"\n[SELF-CORRECT] Phase: Fixing test failures...")
        
        for iteration in range(self.config.max_iterations):
            self.iteration_count = iteration + 1
            
            # Run test and capture output
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.config.project_path,
            )
            
            error_output = result.stderr or result.stdout
            
            print(f"\n  Iteration {iteration + 1}:")
            print(f"  Error: {error_output[:500]}...")
            
            # Ask LLM to fix
            fix_prompt = f"""The tests are failing. Fix the implementation.

FEATURE: {feature}
TEST FILE: {test_file}
IMPLEMENTATION FILE: {implementation_file}

ERROR OUTPUT:
{error_output}

Fix the implementation to make tests pass:
1. Read the error output carefully
2. Identify the root cause
3. Fix ONLY the implementation file
4. Return ONLY the corrected implementation code"""
            
            response = self.llm.invoke(fix_prompt)
            self._write_file(implementation_file, response.content)
            
            # Run test again
            if self._run_test(test_command):
                print(f"  ✓ Tests passed after {iteration + 1} iterations")
                return {
                    "status": "success",
                    "feature": feature,
                    "iterations": iteration + 1,
                    "history": self.history,
                }
        
        return {
            "status": "failed",
            "feature": feature,
            "iterations": self.config.max_iterations,
            "error": "Max iterations reached without passing tests",
        }
    
    def _run_test(self, test_command: str) -> bool:
        """Run tests and return True if passing."""
        try:
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.config.project_path,
                timeout=self.config.timeout,
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def _write_file(self, filepath: str, content: str) -> None:
        """Write content to file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    def _read_file(self, filepath: str) -> str:
        """Read content from file."""
        return Path(filepath).read_text()
    
    def _reset_files(self, *files: str) -> None:
        """Reset files to empty state."""
        for f in files:
            try:
                Path(f).write_text("")
            except Exception:
                pass


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="TDD Agent")
    parser.add_argument("--feature", required=True, help="Feature description")
    parser.add_argument("--test-file", required=True, help="Test file path")
    parser.add_argument("--impl-file", required=True, help="Implementation file path")
    parser.add_argument("--model", default="qwen2.5-coder", help="Model name")
    parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama URL")
    parser.add_argument("--project-path", default="/home/tbaltzakis/cloudless.gr", help="Project path")
    
    args = parser.parse_args()
    
    agent = TDDAgent(TDDConfig(
        model=args.model,
        base_url=args.base_url,
        project_path=args.project_path,
    ))
    
    result = agent.run_tdd(
        feature=args.feature,
        test_file=args.test_file,
        implementation_file=args.impl_file,
    )
    
    print(f"\nResult: {result['status']}")
    print(f"Iterations: {result.get('iterations', 'N/A')}")