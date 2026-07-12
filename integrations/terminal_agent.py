"""
Terminal Execution Agent Module
===============================

Enables AI agents to execute shell commands, parse output, and self-correct.
Implements AI terminal command execution as per best practices.

Usage:
    from integrations.terminal_agent import TerminalAgent
    
    agent = TerminalAgent(
        project_path="/home/tbaltzakis/cloudless.gr",
        sandbox=True,
    )
    
    # Execute command
    result = agent.execute("pnpm test")
    
    # Self-correct based on error
    if result.error:
        fixed_code = agent.fix_error(result.error, "test")
        agent.apply_fix(fixed_code)
"""

import re
import subprocess
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TerminalConfig:
    """Configuration for terminal agent."""
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    sandbox: bool = True
    allowlist: List[str] = field(default_factory=lambda: [
        "npm", "pnpm", "yarn", "node", "python", "uv",
        "git", "ls", "cat", "cd", "pwd",
        "echo", "grep", "sed", "awk",
        "curl", "wget", "head", "tail",
        "find", "grep", "xxd",
    ])
    blocklist: List[str] = field(default_factory=lambda: [
        "rm -rf", "rm -r", "rm -f",  # Dangerous deletions
        "mkfs", "dd", "fdisk",         # Disk operations
        "chmod 777", "chown",          # Permission changes
        "sudo",                        # Privilege escalation
        "netcat", "nc",                # Network tools
        "base64 -d",                   # Encoding tricks
    ])
    timeout: int = 120
    max_retries: int = 3
    llm: Optional[Any] = None


class TerminalAgent:
    """Terminal execution agent with command parsing and self-correction."""
    
    def __init__(self, config: Optional[TerminalConfig] = None):
        self.config = config or TerminalConfig()
        self.execution_history: List[Dict[str, Any]] = []
        self.stdout_history: List[str] = []
        self.stderr_history: List[str] = []
        self.llm = self.config.llm
        
    def execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a shell command.
        
        Args:
            command: Shell command to execute
            cwd: Working directory (defaults to project path)
            
        Returns:
            Result dictionary with stdout, stderr, exit_code, etc.
        """
        # Validate command against allowlist/blocklist
        validation = self._validate_command(command)
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"Command not allowed: {validation['reason']}",
                "command": command,
            }
        
        # Execute command
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd or self.config.project_path,
                timeout=self.config.timeout,
            )
            
            # Record execution
            self.execution_history.append({
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            })
            self.stdout_history.append(result.stdout)
            self.stderr_history.append(result.stderr)
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
                "duration": None,  # Could add timing
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timed out",
                "command": command,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
            }
    
    def _validate_command(self, command: str) -> Dict[str, Any]:
        """Validate command against allowlist/blocklist."""
        command_lower = command.lower()
        
        # Check blocklist first
        for blocked in self.config.blocklist:
            if blocked.lower() in command_lower:
                return {
                    "valid": False,
                    "reason": f"Blocked command: '{blocked}'",
                }
        
        # If allowlist is not empty, check against it
        if self.config.allowlist:
            cmd_base = command.split()[0] if command.split() else ""
            allowed_commands = [c.split()[0] for c in self.config.allowlist]
            if cmd_base not in allowed_commands:
                return {
                    "valid": False,
                    "reason": f"Command '{cmd_base}' not in allowlist",
                }
        
        return {"valid": True}
    
    def parse_output(self, output: str, output_type: str = "generic") -> Dict[str, Any]:
        """
        Parse terminal output to extract structured information.
        
        Args:
            output: Raw output from command
            output_type: Type of output (compiler, test, generic)
            
        Returns:
            Parsed information dictionary
        """
        parsed = {
            "has_errors": False,
            "has_warnings": False,
            "errors": [],
            "warnings": [],
            "summary": {},
        }
        
        if output_type == "compiler":
            parsed = self._parse_compiler_output(output)
        elif output_type == "test":
            parsed = self._parse_test_output(output)
        else:
            parsed = self._parse_generic_output(output)
        
        return parsed
    
    def _parse_compiler_output(self, output: str) -> Dict[str, Any]:
        """Parse compiler output (TypeScript, etc.)."""
        parsed = {
            "has_errors": False,
            "has_warnings": False,
            "errors": [],
            "warnings": [],
        }
        
        # TypeScript/JavaScript error patterns
        error_pattern = r'(error|Error):\s*(.+?)\s*\n.*?at\s*(.+?:\d+:\d+)'
        warning_pattern = r'(warning|Warning):\s*(.+?)\s*\n'
        
        for match in re.finditer(error_pattern, output, re.IGNORECASE):
            parsed["errors"].append({
                "type": match.group(1),
                "message": match.group(2),
                "location": match.group(3),
            })
        
        for match in re.finditer(warning_pattern, output, re.IGNORECASE):
            parsed["warnings"].append({
                "type": match.group(1),
                "message": match.group(2),
            })
        
        parsed["has_errors"] = len(parsed["errors"]) > 0
        parsed["has_warnings"] = len(parsed["warnings"]) > 0
        
        return parsed
    
    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse test runner output (Vitest, Jest, etc.)."""
        parsed = {
            "has_errors": False,
            "failed_tests": [],
            "passed_tests": [],
            "summary": {},
        }
        
        # Test count patterns
        pass_pattern = r'(\d+)\s*pass'
        fail_pattern = r'(\d+)\s*fail'
        total_pattern = r'(\d+)\s*total'
        
        passes = re.search(pass_pattern, output)
        fails = re.search(fail_pattern, output)
        total = re.search(total_pattern, output)
        
        if passes:
            parsed["summary"]["passed"] = int(passes.group(1))
        if fails:
            parsed["summary"]["failed"] = int(fails.group(1))
            parsed["has_errors"] = True
        if total:
            parsed["summary"]["total"] = int(total.group(1))
        
        # Individual test failures
        test_fail_pattern = r'✕\s*(.+?)\s*\n.*?(?:at\s*)?(.+?:\d+)'
        for match in re.finditer(test_fail_pattern, output):
            parsed["failed_tests"].append({
                "name": match.group(1),
                "location": match.group(2),
            })
        
        return parsed
    
    def _parse_generic_output(self, output: str) -> Dict[str, Any]:
        """Parse generic terminal output."""
        return {
            "output": output[:1000],  # Truncate for safety
            "length": len(output),
        }
    
    def fix_error(self, error_output: str, error_type: str = "generic") -> str:
        """
        Generate fix for error output.
        
        Args:
            error_output: Raw error output
            error_type: Type of error (compiler, test, generic)
            
        Returns:
            Suggested fix code
        """
        parsed = self.parse_output(error_output, error_type)
        
        # Build fix prompt
        fix_prompt = f"""Fix the following error in the codebase.

ERROR OUTPUT:
{error_output[:1000]}

PARSED ERRORS:
{parsed}

Fix the implementation to resolve these errors:
1. Read the error carefully
2. Identify the root cause
3. Fix ONLY the problematic code
4. Return ONLY the corrected code"""
        
        # For compiler errors, include file context
        if error_type == "compiler" and parsed["errors"]:
            first_error = parsed["errors"][0]
            if "location" in first_error:
                fix_prompt += f"\n\nERROR LOCATION: {first_error['location']}"
        
        # Use LLM if available
        if self.llm is not None:
            try:
                response = self.llm.invoke(fix_prompt)
                fix = response.content if isinstance(response.content, str) else str(response)
                return fix.strip()
            except Exception as e:
                return f"Failed to generate fix via LLM: {e}"
        
        # Fallback: return structured error summary for manual fixing
        return f"""# Error Analysis
# Type: {error_type}
# Parsed: {parsed}\n#\n# Raw output (truncated):
# {error_output[:500]}..."""
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history."""
        return self.execution_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear execution history."""
        self.execution_history = []
        self.stdout_history = []
        self.stderr_history = []


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Terminal Agent")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--project-path", default="/home/tbaltzakis/cloudless.gr", help="Project path")
    parser.add_argument("--sandbox", action="store_true", help="Enable sandbox mode")
    
    args = parser.parse_args()
    
    agent = TerminalAgent(TerminalConfig(
        project_path=args.project_path,
        sandbox=args.sandbox,
    ))
    
    result = agent.execute(args.command)
    
    print(f"Success: {result['success']}")
    print(f"Exit Code: {result.get('exit_code', 'N/A')}")
    print(f"\nSTDOUT:\n{result.get('stdout', 'N/A')}")
    if result.get('stderr'):
        print(f"\nSTDERR:\n{result.get('stderr', 'N/A')}")