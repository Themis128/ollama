"""
Sandbox Agent Module
====================

Provides isolated execution environment for AI agents with security controls.
Implements sandboxing, command allowlists, and audit logging.

Usage:
    from integrations.sandbox_agent import SandboxAgent
    
    sandbox = SandboxAgent(
        project_path="/home/tbaltzakis/cloudless.gr",
        allow_dangerous=False,
    )
    
    # Execute in sandbox
    result = sandbox.execute("pnpm test")
    
    # Check audit log
    log = sandbox.get_audit_log()
"""

import os
import subprocess
import json
import hashlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import tempfile


@dataclass
class SandboxConfig:
    """Configuration for sandbox agent."""
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    allow_dangerous: bool = False
    enable_isolation: bool = True
    max_output_size: int = 100000
    timeout: int = 120
    audit_log_path: str = "/tmp/sandbox_audit.log"
    
    # Command allowlist
    allowlist: List[str] = field(default_factory=lambda: [
        "npm", "pnpm", "yarn", "node", "python", "uv",
        "git", "ls", "cat", "cd", "pwd", "echo",
        "grep", "sed", "awk", "find", "head", "tail",
        "curl", "wget", "xxd", "stat", "file",
        "npx", "tsx", "tsc", "jest", "vitest",
    ])
    
    # Command blocklist (dangerous commands)
    blocklist: List[str] = field(default_factory=lambda: [
        "rm -rf", "rm -r", "rm -f",
        "mkfs", "dd", "fdisk", "parted",
        "chmod 777", "chown", "chmod +s",
        "sudo", "su -", "pkexec",
        "netcat", "nc -", "ncat",
        "base64 -d", "xxd -r",
        "exec", "eval", "source",
        "bash -c", "sh -c",
        "wget -e", "curl -d",
    ])


class SandboxAgent:
    """Sandbox agent with security controls and audit logging."""
    
    def __init__(self, config: Optional[SandboxConfig] = None):
        self.config = config or SandboxConfig()
        self.audit_log: List[Dict[str, Any]] = []
        self._init_audit_log()
        
    def _init_audit_log(self) -> None:
        """Initialize audit log file."""
        Path(self.config.audit_log_path).parent.mkdir(parents=True, exist_ok=True)
        
    def _add_audit_entry(self, entry: Dict[str, Any]) -> None:
        """Add entry to audit log."""
        self.audit_log.append(entry)
        
        # Also write to file
        with open(self.config.audit_log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def _validate_command(self, command: str) -> Dict[str, Any]:
        """Validate command against allowlist/blocklist."""
        command_lower = command.lower()
        
        # Check blocklist first
        for blocked in self.config.blocklist:
            if blocked.lower() in command_lower:
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "BLOCKED",
                    "command": command,
                    "reason": f"Blocked: '{blocked}' matches blocklist",
                    "status": "DENIED",
                }
                self._add_audit_entry(entry)
                return {"valid": False, "reason": f"Blocked: '{blocked}'"}
        
        # Check allowlist if enabled
        if not self.config.allow_dangerous and self.config.allowlist:
            cmd_base = command.split()[0] if command.split() else ""
            allowed_commands = [c.split()[0] for c in self.config.allowlist]
            if cmd_base not in allowed_commands:
                entry = {
                    "timestamp": datetime.now().isoformat(),
                    "type": "ALLOWLIST_CHECK",
                    "command": command,
                    "reason": f"Command '{cmd_base}' not in allowlist",
                    "status": "DENIED",
                }
                self._add_audit_entry(entry)
                return {"valid": False, "reason": f"Not in allowlist: '{cmd_base}'"}
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "ALLOWLIST_CHECK",
            "command": command,
            "status": "ALLOWED",
        }
        self._add_audit_entry(entry)
        
        return {"valid": True}
    
    def _setup_isolation(self) -> Dict[str, str]:
        """Setup isolated environment if enabled."""
        env = os.environ.copy()
        
        # Clean environment if isolation enabled
        if self.config.enable_isolation:
            # Remove potentially dangerous env vars
            dangerous_vars = [
                "LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH",
                "HOME", "USER", "PATH",  # Keep PATH minimal
            ]
            for var in dangerous_vars:
                env.pop(var, None)
            
            # Set safe minimal environment
            env["PATH"] = "/usr/bin:/bin"
            env["TMPDIR"] = tempfile.gettempdir()
            
        return env
    
    def execute(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute command in sandbox.
        
        Args:
            command: Command to execute
            cwd: Working directory (defaults to project path)
            
        Returns:
            Result dictionary with output, status, and audit info
        """
        # Validate command
        validation = self._validate_command(command)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["reason"],
                "command": command,
            }
        
        # Setup environment
        env = self._setup_isolation()
        
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd or self.config.project_path,
                env=env,
                timeout=self.config.timeout,
            )
            
            # Truncate output if needed
            stdout = result.stdout[:self.config.max_output_size]
            stderr = result.stderr[:self.config.max_output_size]
            
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "EXECUTION",
                "command": command,
                "exit_code": result.returncode,
                "stdout_length": len(result.stdout),
                "stderr_length": len(result.stderr),
                "status": "SUCCESS" if result.returncode == 0 else "FAILED",
            }
            self._add_audit_entry(entry)
            
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "command": command,
                "duration": None,  # Could add timing
            }
            
        except subprocess.TimeoutExpired:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "EXECUTION",
                "command": command,
                "error": "TIMEOUT",
                "status": "FAILED",
            }
            self._add_audit_entry(entry)
            
            return {
                "success": False,
                "error": "Command timed out",
                "command": command,
            }
            
        except Exception as e:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "type": "EXECUTION",
                "command": command,
                "error": str(e),
                "status": "FAILED",
            }
            self._add_audit_entry(entry)
            
            return {
                "success": False,
                "error": str(e),
                "command": command,
            }
    
    def execute_safe(self, command: str, args: List[str]) -> Dict[str, Any]:
        """
        Execute command with safe arguments only.
        
        Args:
            command: Base command
            args: List of safe arguments
            
        Returns:
            Result dictionary
        """
        # Validate each argument
        for arg in args:
            if not self._validate_arg(arg):
                return {
                    "success": False,
                    "error": f"Invalid argument: '{arg}'",
                    "command": command,
                }
        
        full_command = f"{command} {' '.join(args)}"
        return self.execute(full_command)
    
    def _validate_arg(self, arg: str) -> bool:
        """Validate a single argument."""
        # Simple validation - no dangerous characters
        dangerous_chars = [";", "|", "&", "$", "`", ">", "<"]
        if any(c in arg for c in dangerous_chars):
            return False
        
        # No path traversal
        if ".." in arg:
            return False
        
        return True
    
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        return self.audit_log
    
    def clear_audit_log(self) -> None:
        """Clear audit log."""
        self.audit_log = []
        Path(self.config.audit_log_path).write_text("")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get sandbox usage statistics."""
        total = len(self.audit_log)
        blocked = sum(1 for e in self.audit_log if e.get("status") == "DENIED")
        allowed = total - blocked
        failures = sum(1 for e in self.audit_log if e.get("status") == "FAILED")
        
        return {
            "total_executions": total,
            "blocked_commands": blocked,
            "allowed_commands": allowed,
            "failed_executions": failures,
            "success_rate": allowed / total if total > 0 else 1.0,
        }
    
    def export_audit_log(self, filepath: str) -> None:
        """Export audit log to file."""
        with open(filepath, "w") as f:
            json.dump(self.audit_log, f, indent=2)


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sandbox Agent")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("--project-path", default="/home/tbaltzakis/cloudless.gr", help="Project path")
    parser.add_argument("--allow-dangerous", action="store_true", help="Allow dangerous commands")
    parser.add_argument("--show-audit", action="store_true", help="Show audit log after execution")
    
    args = parser.parse_args()
    
    sandbox = SandboxAgent(SandboxConfig(
        project_path=args.project_path,
        allow_dangerous=args.allow_dangerous,
    ))
    
    result = sandbox.execute(args.command)
    
    print(f"Success: {result['success']}")
    if result.get('exit_code') is not None:
        print(f"Exit Code: {result['exit_code']}")
    if result.get('stdout'):
        print(f"\nSTDOUT:\n{result['stdout']}")
    if result.get('stderr'):
        print(f"\nSTDERR:\n{result['stderr']}")
    
    if args.show_audit or not result['success']:
        print(f"\nAudit Log ({len(sandbox.get_audit_log())} entries):")
        for entry in sandbox.get_audit_log():
            print(f"  {entry['timestamp']} [{entry['type']}] {entry.get('status', 'N/A')}: {entry.get('command', 'N/A')}")