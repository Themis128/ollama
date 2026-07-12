"""
Debug Agent Module
===================

Log analysis and self-fixing agent for debugging code errors.

Usage:
    from integrations.debug_agent import DebugAgent
    
    debugger = DebugAgent()
    result = debugger.self_fix(
        error_output="ReferenceError: x is not defined",
        file_path="src/app.ts",
        test_command="pnpm test",
    )
"""

import subprocess
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

from langchain_ollama import ChatOllama  # type: ignore


@dataclass
class DebugConfig:
    """Configuration for Debug agent."""
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    max_iterations: int = 5
    timeout: int = 60


class DebugAgent:
    """Debug agent for log analysis and self-fixing code errors."""
    
    def __init__(self, config: Optional[DebugConfig] = None):
        self.config = config or DebugConfig()
        self.llm = ChatOllama(
            model=self.config.model,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
        )
        
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with prompt and return response content."""
        response = self.llm.invoke(prompt)
        return response.content if isinstance(response.content, str) else ""
    
    def self_fix(
        self,
        error_output: str,
        file_path: str,
        test_command: str,
    ) -> Dict[str, Any]:
        """
        Self-fix code errors by analyzing error output and applying fixes.
        
        Args:
            error_output: The error message from the test/command
            file_path: Path to the file to fix
            test_command: Command to run tests to verify fix
            
        Returns:
            Result dictionary with fix_generated, fix_applied, test_passed status
        """
        try:
            # Read current file content
            original_content = Path(file_path).read_text()
            
            # Generate fix prompt
            prompt = f"""Fix the error in the code file.

ERROR:
{error_output}

FILE: {file_path}

ORIGINAL CODE:
{original_content}

Fix the code to resolve the error. Return ONLY the corrected code with no explanation."""
            
            fix_content = self._invoke_llm(prompt)
            
            # Write fixed code (preserve trailing newline if present in original)
            if original_content.endswith('\n') and not fix_content.endswith('\n'):
                fix_content += '\n'
            Path(file_path).write_text(fix_content)
            
            # Run test to verify
            result = subprocess.run(
                test_command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.config.project_path,
                timeout=self.config.timeout,
            )
            
            test_passed = result.returncode == 0
            
            return {
                "fix_generated": fix_content,
                "fix_applied": True,
                "test_passed": test_passed,
            }
        except Exception as e:
            logging.error(f"DebugAgent self_fix failed: {e}")
            return {
                "fix_generated": None,
                "fix_applied": False,
                "test_passed": False,
                "error": str(e),
            }