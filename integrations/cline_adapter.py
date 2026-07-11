"""
Cline-compatible Agent Adapter
=================================

Provides a JSON-based interface for Cline-like applications to interact with
DeepAgents + Ollama integration.

Features:
- Cline-compatible tool calling format
- JSON-RPC style communication
- File system operations
- Terminal command execution
- Project context management
"""

import json
import os
import subprocess
from typing import Any, Dict, List, Optional
from pathlib import Path


class ClineAdapter:
    """Provide Cline-compatible tool interface for DeepAgents + Ollama."""

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = project_path or os.environ.get("PROJECT_PATH", os.getcwd())
        self.available_tools = [
            "list_files",
            "read_file",
            "write_file",
            "run_command",
            "ask_agent",
            "list_models",
            "pull_model",
            "check_ollama",
            "search_files",
            "get_file_info",
            "analyze_code",
            "generate_test",
        ]

    def run_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool and return Cline-compatible response."""
        if tool_name not in self.available_tools:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "available_tools": self.available_tools,
            }

        method = getattr(self, f"_tool_{tool_name}", None)
        if method is None:
            return {"success": False, "error": f"Tool method not found: {tool_name}"}
        return method(params)

    def _tool_list_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List files in a directory (Cline compatible)."""
        path = params.get("path", self.project_path)
        max_depth = params.get("max_depth", 3)

        try:
            p = Path(path)
            if not p.exists():
                return {"success": False, "error": f"Path not found: {path}"}

            files = []
            for item in p.rglob("*"):
                if len(item.parts) - len(p.parts) <= max_depth:
                    files.append({
                        "path": str(item),
                        "relative": str(item.relative_to(p)) if item.is_relative_to(p) else str(item),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None,
                    })

            return {"success": True, "files": sorted(files, key=lambda x: x["path"])}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_read_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read file content (Cline compatible)."""
        file_path = params.get("path")
        if not file_path:
            return {"success": False, "error": "Missing path parameter"}

        try:
            p = Path(file_path)
            if not p.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            content = p.read_text(encoding="utf-8", errors="replace")
            return {
                "success": True,
                "content": content,
                "path": str(p),
                "lines": content.count("\n") + 1,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_write_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write file content (Cline compatible)."""
        file_path = params.get("path")
        content = params.get("content")
        if not file_path or content is None:
            return {"success": False, "error": "Missing path or content parameter"}

        try:
            p = Path(file_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return {
                "success": True,
                "path": str(p),
                "bytes_written": len(content.encode("utf-8")),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_run_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run terminal command (Cline compatible)."""
        command = params.get("command")
        cwd = params.get("cwd", self.project_path)
        timeout = params.get("timeout", 30000)

        if not command:
            return {"success": False, "error": "Missing command parameter"}

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout / 1000,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_ask_agent(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Ask Ollama agent a question (Cline compatible)."""
        prompt = params.get("prompt")
        model = params.get("model", os.environ.get("OLLAMA_MODEL", "qwen2.5-coder"))
        base_url = params.get("url", os.environ.get("OLLAMA_URL", "http://localhost:11434"))

        if not prompt:
            return {"success": False, "error": "Missing prompt parameter"}

        try:
            from langchain_ollama import ChatOllama

            llm = ChatOllama(
                model=model,
                base_url=base_url,
                temperature=0.1,
                max_tokens=4096,
            )

            response = llm.invoke(prompt)
            content = response.content if isinstance(response.content, str) else ""

            return {
                "success": True,
                "response": content,
                "model": model,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_list_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List available Ollama models."""
        import httpx

        base_url = params.get("url", os.environ.get("OLLAMA_URL", "http://localhost:11434"))

        try:
            response = httpx.get(f"{base_url}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()

            models = []
            for m in data.get("models", []):
                models.append({
                    "name": m.get("name", "unknown"),
                    "size_gb": round(m.get("size", 0) / (1024**3), 2),
                    "modified": m.get("modified_at", ""),
                })

            return {"success": True, "models": models}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_pull_model(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Pull an Ollama model."""
        model = params.get("model", "qwen2.5-coder")

        try:
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True,
                text=True,
            )
            return {
                "success": result.returncode == 0,
                "model": model,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_check_ollama(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check Ollama server status."""
        import httpx

        base_url = params.get("url", os.environ.get("OLLAMA_URL", "http://localhost:11434"))

        try:
            response = httpx.get(f"{base_url}/api/tags", timeout=5)
            return {
                "success": response.status_code == 200,
                "status": "running" if response.status_code == 200 else "error",
                "url": base_url,
            }
        except Exception as e:
            return {
                "success": False,
                "status": "not_running",
                "error": str(e),
                "url": base_url,
            }

    def _tool_search_files(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search for files matching a pattern."""
        pattern = params.get("pattern", "*.ts")
        directory = params.get("directory", self.project_path)

        try:
            p = Path(directory)
            if not p.exists():
                return {"success": False, "error": f"Directory not found: {directory}"}

            matches = []
            for item in p.rglob(pattern):
                matches.append({
                    "path": str(item),
                    "relative": str(item.relative_to(p)) if item.is_relative_to(p) else str(item),
                })

            return {
                "success": True,
                "matches": sorted(matches, key=lambda x: x["path"]),
                "count": len(matches),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_get_file_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed file information."""
        file_path = params.get("path")

        if not file_path:
            return {"success": False, "error": "Missing path parameter"}

        try:
            p = Path(file_path)
            if not p.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            stat = p.stat()
            return {
                "success": True,
                "path": str(p),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "is_file": p.is_file(),
                "is_dir": p.is_dir(),
                "extension": p.suffix if p.is_file() else None,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_analyze_code(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code structure and quality."""
        path = params.get("path", self.project_path)
        focus = params.get("focus", "general")

        try:
            p = Path(path)
            if not p.exists():
                return {"success": False, "error": f"Path not found: {path}"}

            # Count files by type
            file_types = {}
            for item in p.rglob("*"):
                if item.is_file():
                    ext = item.suffix or "no_extension"
                    file_types[ext] = file_types.get(ext, 0) + 1

            # Identify key files
            key_files = []
            for name in ["package.json", "tsconfig.json", "next.config.mjs", "README.md"]:
                if (p / name).exists():
                    key_files.append(name)

            return {
                "success": True,
                "path": str(p),
                "file_types": file_types,
                "total_files": sum(file_types.values()),
                "key_files": key_files,
                "focus_areas": [focus] if focus != "general" else ["structure", "dependencies", "config"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_generate_test(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test scaffolding for a file."""
        file_path = params.get("path")
        test_framework = params.get("framework", "vitest")

        if not file_path:
            return {"success": False, "error": "Missing path parameter"}

        try:
            p = Path(file_path)
            if not p.exists():
                return {"success": False, "error": f"File not found: {file_path}"}

            # Generate test file path
            test_path = p.parent / f"{p.stem}.test.{p.suffix.lstrip('.')}"

            return {
                "success": True,
                "source_file": str(p),
                "test_file": str(test_path),
                "framework": test_framework,
                "template_available": test_framework in ["vitest", "jest", "playwright"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cline Adapter for Ollama")
    parser.add_argument("--tool", required=True, help="Tool name to execute")
    parser.add_argument("--params", help="JSON parameters")
    parser.add_argument("--project-path", help="Project path context")

    args = parser.parse_args()
    adapter = ClineAdapter(args.project_path)
    params = json.loads(args.params) if args.params else {}

    result = adapter.run_tool(args.tool, params)
    print(json.dumps(result, indent=2))