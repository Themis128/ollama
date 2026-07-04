"""
Debug Agent Module
==================

Enables AI agents to analyze logs, diagnose errors, and self-fix issues.
Implements proactive debugging capabilities.

Usage:
    from integrations.debug_agent import DebugAgent
    
    debugger = DebugAgent(
        model="qwen2.5-coder",
        base_url="http://localhost:11434",
    )
    
    # Analyze error
    diagnosis = debugger.analyze_error(error_output, file_path)
    
    # Proactive log analysis
    issues = debugger.analyze_logs(log_file)
    
    # Self-fix code
    fix = debugger.generate_fix(error_output, implementation_file)
"""

import os
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

from langchain_ollama import ChatOllama


@dataclass
class DebugConfig:
    """Configuration for debug agent."""
    model: str = "qwen2.5-coder"
    base_url: str = "http://localhost:11434"
    project_path: str = "/home/tbaltzakis/cloudless.gr"
    temperature: float = 0.1
    max_analysis_lines: int = 1000


class DebugAgent:
    """Debug agent with log analysis and self-fixing capabilities."""
    
    def __init__(self, config: Optional[DebugConfig] = None):
        self.config = config or DebugConfig()
        self.analysis_history: List[Dict[str, Any]] = []
        
    def analyze_error(
        self,
        error_output: str,
        file_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze error output and provide diagnosis.
        
        Args:
            error_output: Raw error output
            file_path: Path to file where error occurred
            
        Returns:
            Diagnosis dictionary with root cause and suggested fix
        """
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "error_type": self._classify_error(error_output),
            "root_cause": self._identify_root_cause(error_output, file_path),
            "location": self._extract_location(error_output, file_path),
            "suggested_fix": self._suggest_fix(error_output),
            "related_files": self._identify_related_files(error_output),
            "severity": self._assess_severity(error_output),
        }
        
        self.analysis_history.append(diagnosis)
        return diagnosis
    
    def _classify_error(self, error_output: str) -> str:
        """Classify the type of error."""
        error_lower = error_output.lower()
        
        if "typeerror" in error_lower or "type" in error_lower:
            return "type_error"
        elif "syntaxerror" in error_lower or "syntax" in error_lower:
            return "syntax_error"
        elif "importerror" in error_lower or "module" in error_lower:
            return "import_error"
        elif "attributeerror" in error_lower or "attribute" in error_lower:
            return "attribute_error"
        elif "keyerror" in error_lower or "key" in error_lower:
            return "key_error"
        elif "indexerror" in error_lower or "index" in error_lower:
            return "index_error"
        elif "test" in error_lower and ("fail" in error_lower or "error" in error_lower):
            return "test_failure"
        elif "compile" in error_lower or "build" in error_lower:
            return "compilation_error"
        else:
            return "runtime_error"
    
    def _identify_root_cause(self, error_output: str, file_path: Optional[str] = None) -> str:
        """Identify the root cause of the error."""
        prompt = f"""Analyze the following error and identify the root cause.

ERROR OUTPUT:
{error_output[:2000]}

{"FILE: " + file_path if file_path else ""}

Provide a concise root cause analysis. Focus on what's actually broken."""
        
        response = self._invoke_llm(prompt)
        return response.strip()
    
    def _extract_location(self, error_output: str, file_path: Optional[str] = None) -> Dict[str, Any]:
        """Extract location information from error."""
        location = {
            "file": file_path or "unknown",
            "line": None,
            "function": None,
        }
        
        # Try to extract line number from error
        line_patterns = [
            r"line\s+(\d+)",
            r":(\d+):",
            r"at\s+\w+\s+\(.*:(\d+)\)",
        ]
        
        for pattern in line_patterns:
            match = re.search(pattern, error_output)
            if match:
                location["line"] = int(match.group(1))
                break
        
        # Try to extract function name
        func_patterns = [
            r"in\s+(\w+)\s*\(",
            r"function\s+(\w+)",
            r"at\s+(\w+)",
        ]
        
        for pattern in func_patterns:
            match = re.search(pattern, error_output)
            if match:
                location["function"] = match.group(1)
                break
        
        return location
    
    def _suggest_fix(self, error_output: str) -> str:
        """Suggest a fix for the error."""
        prompt = f"""Suggest a fix for the following error.

ERROR OUTPUT:
{error_output[:2000]}

Provide a concise fix suggestion or code snippet."""
        
        response = self._invoke_llm(prompt)
        return response.strip()
    
    def _identify_related_files(self, error_output: str) -> List[str]:
        """Identify files related to the error."""
        # Extract filenames from error output
        file_patterns = [
            r"(/[^:\s]+:\d+:)",
            r"from\s+['\"]([^'\"]+)['\"]",
            r"import\s+['\"]([^'\"]+)['\"]",
        ]
        
        related_files = []
        for pattern in file_patterns:
            matches = re.findall(pattern, error_output)
            related_files.extend(matches)
        
        return list(set(related_files))[:5]
    
    def _assess_severity(self, error_output: str) -> str:
        """Assess the severity of the error."""
        error_lower = error_output.lower()
        
        if any(word in error_lower for word in ["panic", "fatal", "crash", "segfault"]):
            return "critical"
        elif any(word in error_lower for word in ["error", "fail", "exception"]):
            return "high"
        elif any(word in error_lower for word in ["warning", "deprecated"]):
            return "medium"
        else:
            return "low"
    
    def analyze_logs(
        self,
        log_file: str,
        max_lines: int = 1000,
    ) -> Dict[str, Any]:
        """
        Analyze log file for issues.
        
        Args:
            log_file: Path to log file
            max_lines: Maximum lines to analyze
            
        Returns:
            Analysis results dictionary
        """
        analysis = {
            "file": log_file,
            "timestamp": datetime.now().isoformat(),
            "total_lines": 0,
            "issues_found": [],
            "patterns_detected": [],
            "summary": "",
        }
        
        try:
            path = Path(log_file)
            lines = path.read_text().split("\n")[:max_lines]
            analysis["total_lines"] = len(lines)
            
            # Detect patterns
            patterns = {
                "errors": r"error|ERROR|Error",
                "warnings": r"warning|WARNING|Warning|warn",
                "exceptions": r"exception|Exception|EXCEPTION",
                "stacktraces": r"at\s+\w+|Traceback|Stack trace",
                "timeouts": r"timeout|timed out|deadline exceeded",
                "connection": r"connection|network|socket",
                "memory": r"memory|oom|heap",
            }
            
            for pattern_name, pattern in patterns.items():
                matches = [line for line in lines if re.search(pattern, line, re.IGNORECASE)]
                if matches:
                    analysis["patterns_detected"].append({
                        "pattern": pattern_name,
                        "count": len(matches),
                        "examples": matches[:3],
                    })
                    for match in matches[:2]:
                        analysis["issues_found"].append({
                            "type": pattern_name,
                            "line": match,
                        })
            
            # Generate summary
            if analysis["patterns_detected"]:
                total_issues = sum(p["count"] for p in analysis["patterns_detected"])
                analysis["summary"] = f"Found {total_issues} issues across {len(analysis['patterns_detected'])} pattern categories"
            else:
                analysis["summary"] = "No issues detected in log file"
                
        except Exception as e:
            analysis["summary"] = f"Error reading log file: {str(e)}"
        
        self.analysis_history.append(analysis)
        return analysis
    
    def generate_fix(
        self,
        error_output: str,
        file_path: str,
        implementation: Optional[str] = None,
    ) -> str:
        """
        Generate fix for error.
        
        Args:
            error_output: Error output
            file_path: Path to file to fix
            implementation: Current implementation code
            
        Returns:
            Fixed code
        """
        context = ""
        if implementation:
            context = f"\n\nCURRENT IMPLEMENTATION:\n{implementation}"
        
        prompt = f"""Fix the error in the following code.

ERROR OUTPUT:
{error_output[:2000]}

FILE: {file_path}{context}

Fix the implementation to resolve the error. Return ONLY the corrected code."""
        
        response = self._invoke_llm(prompt)
        return response.strip()
    
    def self_fix(
        self,
        error_output: str,
        file_path: str,
        test_command: str = "pnpm test",
    ) -> Dict[str, Any]:
        """
        Attempt to self-fix an error.
        
        Args:
            error_output: Error output
            file_path: Path to file to fix
            test_command: Command to run tests
            
        Returns:
            Result dictionary with fix attempt status
        """
        result = {
            "success": False,
            "error": error_output,
            "file": file_path,
            "fix_generated": None,
            "fix_applied": False,
            "test_passed": False,
        }
        
        # Generate fix
        fix = self.generate_fix(error_output, file_path)
        result["fix_generated"] = fix
        
        # Apply fix (in real implementation, write to file)
        # result["fix_applied"] = True
        
        # Test the fix
        # if result["fix_applied"]:
        #     # Run test_command and check if it passes
        #     pass
        
        return result
    
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with prompt."""
        llm = ChatOllama(
            model=self.config.model,
            temperature=self.config.temperature,
            base_url=self.config.base_url,
        )
        response = llm.invoke(prompt)
        return response.content
    
    def get_analysis_history(self) -> List[Dict[str, Any]]:
        """Get analysis history."""
        return self.analysis_history


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug Agent")
    parser.add_argument("--error", help="Error output to analyze")
    parser.add_argument("--file", help="File path for error")
    parser.add_argument("--log", help="Log file to analyze")
    parser.add_argument("--model", default="qwen2.5-coder", help="Model name")
    parser.add_argument("--base-url", default="http://localhost:11434", help="Ollama URL")
    
    args = parser.parse_args()
    
    debugger = DebugAgent(DebugConfig(
        model=args.model,
        base_url=args.base_url,
    ))
    
    if args.error:
        diagnosis = debugger.analyze_error(args.error, args.file)
        print(f"\n{'='*60}")
        print("DIAGNOSIS")
        print(f"{'='*60}")
        print(f"Error Type: {diagnosis['error_type']}")
        print(f"Root Cause: {diagnosis['root_cause']}")
        print(f"Location: {diagnosis['location']}")
        print(f"Suggested Fix: {diagnosis['suggested_fix']}")
        print(f"Severity: {diagnosis['severity']}")
        
    elif args.log:
        analysis = debugger.analyze_logs(args.log)
        print(f"\n{'='*60}")
        print("LOG ANALYSIS")
        print(f"{'='*60}")
        print(f"File: {analysis['file']}")
        print(f"Lines: {analysis['total_lines']}")
        print(f"Summary: {analysis['summary']}")
        if analysis['patterns_detected']:
            print(f"\nPatterns Detected:")
            for p in analysis['patterns_detected'][:5]:
                print(f"  - {p['pattern']}: {p['count']} occurrences")