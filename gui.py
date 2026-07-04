#!/usr/bin/env python3
"""
DeepAgents + Ollama GUI Interface
==================================

A modern terminal-based GUI for interacting with agents using natural language.

Features:
- Ollama server management (start/stop/pull models)
- Project connection and detection
- Natural language commands with NLP auto-detection
- Multi-agent orchestration
- Enhanced web research
- Modern UI with prompt_toolkit (optional)

Usage:
    python3 gui.py
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

# Try to import prompt_toolkit for modern UI
try:
    import importlib.util

    HAS_PROMPT_TOOLKIT = importlib.util.find_spec("prompt_toolkit") is not None
except ImportError:
    HAS_PROMPT_TOOLKIT = False

if HAS_PROMPT_TOOLKIT:
    from prompt_toolkit import PromptSession

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations import (
    TDDAgent,
    TerminalAgent,
    SandboxAgent,
    Orchestrator,
    WebAgent,
    DebugAgent,
    AgentStorm,
)

# Try to import colorama for cross-platform colors
try:
    from colorama import init, Fore, Style

    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Fallback colors
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    
    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        RESET_ALL = '\033[0m'


class AgentGUI:
    """Modern terminal-based GUI for natural language agent interaction."""
    
    def __init__(self):
        self.orchestrator = Orchestrator()
        self.sandbox = SandboxAgent()
        self.terminal = TerminalAgent()
        self.web = WebAgent()
        self.debugger = DebugAgent()
        self.storm = AgentStorm()
        self.tdd = TDDAgent()
        
        # Ollama server management
        self.ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.environ.get('OLLAMA_MODEL', 'qwen2.5-coder')
        self.ollama_running = self._check_ollama_server()
        
        # Project management
        self.project_path = os.environ.get('PROJECT_PATH', os.getcwd())
        self.project_name = os.environ.get('PROJECT_NAME', 'Unknown')
        self.project_type = os.environ.get('PROJECT_TYPE', 'Unknown')
        
        # UI settings
        self.show_timestamps = True
        self.show_breadcrumbs = True
        self.max_output_length = 4000
        
        # Session management (for prompt_toolkit)
        self.session: Optional[PromptSession] = None
        
        self.history = []
        self.running = True
        
    def _check_ollama_server(self) -> bool:
        """Check if Ollama server is running."""
        try:
            import urllib.request
            import json
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get('models', []) is not None
        except Exception:
            return False
    
    def _start_ollama_server(self) -> Dict[str, Any]:
        """Start Ollama server."""
        result = {'success': False, 'message': ''}
        
        try:
            # Try to start Ollama daemon
            process = subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            # Wait a moment for server to start
            import time
            time.sleep(3)
            
            if self._check_ollama_server():
                result['success'] = True
                result['message'] = 'Ollama server started successfully'
                result['pid'] = process.pid
            else:
                result['message'] = 'Failed to start Ollama server'
                
        except FileNotFoundError:
            result['message'] = 'Ollama not found. Please install Ollama first.'
        except Exception as e:
            result['message'] = f'Error starting Ollama: {str(e)}'
            
        return result
    
    def _stop_ollama_server(self) -> Dict[str, Any]:
        """Stop Ollama server."""
        result = {'success': False, 'message': ''}
        
        try:
            # Kill the ollama process
            subprocess.run(['pkill', '-f', 'ollama serve'], 
                          capture_output=True, timeout=5)
            
            import time
            time.sleep(2)
            
            if not self._check_ollama_server():
                result['success'] = True
                result['message'] = 'Ollama server stopped'
            else:
                result['message'] = 'Failed to stop Ollama server'
                
        except Exception as e:
            result['message'] = f'Error stopping Ollama: {str(e)}'
            
        return result
    
    def _pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model from Ollama library."""
        result = {'success': False, 'message': ''}
        
        try:
            # Show nice progress display
            print(f"\n{Fore.CYAN}┌{'─' * 58}┐{Style.RESET_ALL}")
            print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Pulling Model: {model_name}{Style.RESET_ALL}{' ' * (42 - len(model_name))}{Fore.CYAN}│{Style.RESET_ALL}")
            print(f"{Fore.CYAN}└{'─' * 58}┘{Style.RESET_ALL}\n")
            
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Display progress bar simulation
            import time
            spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            spinner_idx = 0
            
            for line in process.stdout:
                print(f"  {Fore.YELLOW}{spinner[spinner_idx % len(spinner)]}{Style.RESET_ALL} {line.strip()}")
                spinner_idx += 1
                time.sleep(0.1)
            
            process.wait()
            
            if process.returncode == 0:
                result['success'] = True
                result['message'] = f'Model {model_name} pulled successfully'
                print(f"\n{Fore.GREEN}✓ Model pulled successfully{Style.RESET_ALL}")
            else:
                result['message'] = f'Failed to pull model {model_name}'
                print(f"\n{Fore.RED}✗ Failed to pull model{Style.RESET_ALL}")
                
        except FileNotFoundError:
            result['message'] = 'Ollama not found. Please install Ollama first.'
        except Exception as e:
            result['message'] = f'Error pulling model: {str(e)}'
            
        return result
    
    def _list_models(self) -> List[Dict[str, str]]:
        """List available Ollama models."""
        try:
            import urllib.request
            import json
            
            req = urllib.request.Request(f"{self.ollama_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                return data.get('models', [])
        except Exception:
            return []
    
    def _set_project(self, project_path: str) -> Dict[str, Any]:
        """Set the working project."""
        result = {'success': False, 'message': ''}
        
        path = Path(project_path)
        
        if not path.exists():
            result['message'] = f'Project path does not exist: {project_path}'
            return result
        
        if not path.is_dir():
            result['message'] = f'Project path is not a directory: {project_path}'
            return result
        
        # Detect project type
        if (path / 'package.json').exists():
            result['type'] = 'Node.js'
            result['name'] = self._get_package_name(path)
        elif (path / 'pyproject.toml').exists():
            result['type'] = 'Python'
            result['name'] = path.name
        elif (path / 'requirements.txt').exists():
            result['type'] = 'Python'
            result['name'] = path.name
        elif (path / 'Cargo.toml').exists():
            result['type'] = 'Rust'
            result['name'] = path.name
        else:
            result['type'] = 'Unknown'
            result['name'] = path.name
        
        result['success'] = True
        result['path'] = str(path)
        result['message'] = f'Project set to: {result["name"]} ({result["type"]})'
        
        return result
    
    def _get_package_name(self, path: Path) -> str:
        """Get package name from package.json."""
        try:
            with open(path / 'package.json') as f:
                data = json.load(f)
                return data.get('name', path.name)
        except Exception:
            return path.name
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Print the modern GUI header."""
        print()
        # Draw modern header box
        print(f"{Fore.CYAN}╔{'═' * 58}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}┌─────────────────────────────────────────────┐{Style.RESET_ALL}{' ' * 6}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}│ DeepAgents + Ollama - AI Coding Assistant   │{Style.RESET_ALL}{' ' * 3}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}└─────────────────────────────────────────────┘{Style.RESET_ALL}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
        
        # Project info
        proj_info = f"Project: {self.project_name} ({self.project_type})"
        if len(proj_info) > 54:
            proj_info = proj_info[:51] + "..."
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.GREEN}●{Style.RESET_ALL} {proj_info:<54}{Fore.CYAN}║{Style.RESET_ALL}")
        
        # Ollama status
        ollama_status = f"Ollama: {'Running' if self.ollama_running else 'Stopped'}"
        ollama_color = Fore.GREEN if self.ollama_running else Fore.RED
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {ollama_color}●{Style.RESET_ALL} {ollama_status:<54}{Fore.CYAN}║{Style.RESET_ALL}")
        
        # Model info
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.BLUE}●{Style.RESET_ALL} Model: {self.ollama_model:<48}{Fore.CYAN}║{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}╚{'═' * 58}╝{Style.RESET_ALL}")
        print()
    
    def print_help(self):
        """Print modern formatted help."""
        print()
        print(f"{Fore.CYAN}╔{'═' * 58}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Available Commands{Style.RESET_ALL}{' ' * 41}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
        
        # Development commands
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Development{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Create a new [feature/component/API endpoint]")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Implement [functionality] with tests")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Add [feature] to [module]")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Refactor [code/module]")
        
        # Testing commands
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Testing{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Run tests")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Run tests and fix failures")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Run build")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Check for errors")
        
        # Analysis commands
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Analysis (NLP Auto-Detect){Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • analyze codebase")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • check for issues")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • review code")
        
        # Code generation
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Code Generation (NLP Auto-Detect){Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • create API endpoint")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • add component")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • build function")
        
        # Research
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Research (Enhanced Web){Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Research [topic]")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Find documentation for [API/library]")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • Search for [query]")
        
        # Ollama management
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Ollama Management{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • start ollama | stop ollama | check ollama")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • pull [model] | list models")
        
        # Project management
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}Project Management{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • connect [path] | scan projects")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • current")
        
        # System
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}System{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • help | history | clear | project")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}   • exit / quit")
        
        print(f"{Fore.CYAN}╚{'═' * 58}╝{Style.RESET_ALL}")
        print()
    
    def print_project_info(self):
        """Print current project information."""
        print()
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Project Information:{Style.RESET_ALL}")
        print()
        print(f"  Name: {self.project_name}")
        print(f"  Type: {self.project_type}")
        print(f"  Path: {self.project_path}")
        print()
        
        # Check for key files
        if os.path.exists(os.path.join(self.project_path, 'package.json')):
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} package.json found")
        if os.path.exists(os.path.join(self.project_path, '.git')):
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} Git repository")
        if os.path.exists(os.path.join(self.project_path, '.deepagents')):
            print(f"  {Fore.GREEN}✓{Style.RESET_ALL} DeepAgents configured")
        
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def print_history(self):
        """Print command history."""
        print()
        print(f"{Fore.YELLOW}Command History:{Style.RESET_ALL}")
        print()
        if not self.history:
            print("  No commands yet.")
        else:
            for i, entry in enumerate(self.history[-10:], 1):
                print(f"  {i}. {entry['command'][:50]}...")
        print()
    
    def parse_command(self, command):
        """Parse natural language command and determine action."""
        command_lower = command.lower().strip()
        
        # System commands
        if command_lower in ['exit', 'quit', 'q']:
            return {'action': 'exit'}
        if command_lower == 'help':
            return {'action': 'help'}
        if command_lower == 'clear':
            return {'action': 'clear'}
        if command_lower == 'history':
            return {'action': 'history'}
        if command_lower == 'project':
            return {'action': 'project'}
        if command_lower == 'current':
            return {'action': 'current'}
        
        # Ollama commands
        if command_lower in ['start ollama', 'start the ollama server']:
            return {'action': 'start_ollama'}
        if command_lower in ['stop ollama', 'stop the ollama server']:
            return {'action': 'stop_ollama'}
        if command_lower in ['check ollama', 'status ollama', 'ollama status']:
            return {'action': 'check_ollama'}
        if command_lower.startswith('pull ') or command_lower.startswith('pull model '):
            model = command.replace('pull ', '').replace('pull model ', '').strip()
            return {'action': 'pull_model', 'model': model}
        if command_lower in ['list models', 'show models', 'available models']:
            return {'action': 'list_models'}
        
        # Project commands
        if command_lower.startswith('connect ') or command_lower.startswith('connect to '):
            path = command.replace('connect ', '').replace('connect to ', '').strip()
            return {'action': 'connect_project', 'path': path}
        if command_lower in ['scan projects', 'scan for projects', 'list projects']:
            return {'action': 'scan_projects'}
        
        # Test commands
        if 'run test' in command_lower or 'run the test' in command_lower:
            if 'fix' in command_lower:
                return {'action': 'test_and_fix', 'command': command}
            return {'action': 'test', 'command': command}
        
        # Build commands
        if 'run build' in command_lower or 'build the project' in command_lower:
            return {'action': 'build', 'command': command}
        
        # Research commands
        if command_lower.startswith('research ') or 'research for' in command_lower:
            topic = command.replace('research', '').replace('Research', '').strip()
            return {'action': 'research', 'topic': topic}
        
        if command_lower.startswith('search ') or 'search for' in command_lower:
            query = command.replace('search', '').replace('Search', '').replace('for', '').strip()
            return {'action': 'search', 'query': query}
        
        if 'documentation for' in command_lower or 'docs for' in command_lower:
            api = command.split('for')[-1].strip()
            return {'action': 'docs', 'api': api}
        
        # Codebase analysis commands - auto-detect and use current project
        if 'codebase' in command_lower and ('analyze' in command_lower or 'review' in command_lower or 'issues' in command_lower):
            return {'action': 'analyze_codebase', 'command': command}
        
        if 'interactive search' in command_lower or 'search interactive' in command_lower:
            query = command.replace('interactive search', '').replace('search interactive', '').strip()
            return {'action': 'search_interactive', 'query': query}
        
        # Code generation/implementation commands - auto-detect
        if 'create' in command_lower or 'add' in command_lower or 'build' in command_lower or 'implement' in command_lower:
            if any(kw in command_lower for kw in ['api', 'endpoint', 'route', 'function', 'component', 'feature']):
                return {'action': 'generate_code', 'command': command}
        
        # Multi-agent commands
        if 'storm' in command_lower or 'multiple perspectives' in command_lower or 'multi agent' in command_lower:
            return {'action': 'storm', 'command': command}
        
        if 'design' in command_lower and ('with' in command_lower or 'architect' in command_lower):
            return {'action': 'design', 'command': command}
        
        # TDD commands
        if 'implement' in command_lower and 'test' in command_lower:
            return {'action': 'tdd', 'command': command}
        
        # Analysis commands with better NLP detection
        analysis_keywords = [
            'analyze', 'review', 'check for issues', 'find issues', 
            'report', 'assessment', 'audit', 'examine', 'inspect'
        ]
        if any(kw in command_lower for kw in analysis_keywords):
            return {'action': 'analyze_codebase', 'command': command}
        
        # Check for errors
        if 'check for error' in command_lower or 'find error' in command_lower or 'fix error' in command_lower:
            return {'action': 'check_errors', 'command': command}
        
        # Explicit ask/chat shortcut
        if command_lower.startswith('ask ') or command_lower.startswith('chat '):
            return {'action': 'ask', 'command': command}

        # Default: route general prompts through local Ollama agent
        return {'action': 'ask', 'command': command}
    
    def execute_action(self, parsed):
        """Execute the parsed action."""
        action = parsed.get('action')
        
        if action == 'exit':
            print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}\n")
            self.running = False
            return
        
        if action == 'help':
            self.print_help()
            return
        
        if action == 'clear':
            self.clear_screen()
            self.print_header()
            return
        
        if action == 'history':
            self.print_history()
            return
        
        if action == 'project':
            self.print_project_info()
            return
        
        if action == 'current':
            print()
            print(f"{Fore.CYAN}╔{'═' * 58}╗{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.YELLOW}{Style.BRIGHT}Current Configuration{Style.RESET_ALL}{' ' * 31}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}   Project: {self.project_name:<43}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}   Type: {self.project_type:<47}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}   Path: {self.project_path:<45}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}   Ollama: {'Running' if self.ollama_running else 'Stopped':<44}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}   Model: {self.ollama_model:<45}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}║{Style.RESET_ALL}   URL: {self.ollama_url:<47}{Fore.CYAN}║{Style.RESET_ALL}")
            print(f"{Fore.CYAN}╚{'═' * 58}╝{Style.RESET_ALL}")
            print()
            return
        
        if action == 'start_ollama':
            result = self._start_ollama_server()
            if result['success']:
                self.ollama_running = True
                print(f"\n{Fore.GREEN}┌{'─' * 58}┐{Style.RESET_ALL}")
                print(f"{Fore.GREEN}│{Style.RESET_ALL} {Style.BRIGHT}✓ Ollama server started successfully{Style.RESET_ALL}{' ' * 24}{Fore.GREEN}│{Style.RESET_ALL}")
                print(f"{Fore.GREEN}└{'─' * 58}┘{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}┌{'─' * 58}┐{Style.RESET_ALL}")
                print(f"{Fore.RED}│{Style.RESET_ALL} {Style.BRIGHT}✗ {result['message']}{Style.RESET_ALL}{' ' * (58 - len(result['message']) - 2)}{Fore.RED}│{Style.RESET_ALL}")
                print(f"{Fore.RED}└{'─' * 58}┘{Style.RESET_ALL}")
            return
        
        if action == 'stop_ollama':
            result = self._stop_ollama_server()
            if result['success']:
                self.ollama_running = False
                print(f"\n{Fore.GREEN}┌{'─' * 58}┐{Style.RESET_ALL}")
                print(f"{Fore.GREEN}│{Style.RESET_ALL} {Style.BRIGHT}✓ Ollama server stopped{Style.RESET_ALL}{' ' * 32}{Fore.GREEN}│{Style.RESET_ALL}")
                print(f"{Fore.GREEN}└{'─' * 58}┘{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}┌{'─' * 58}┐{Style.RESET_ALL}")
                print(f"{Fore.RED}│{Style.RESET_ALL} {Style.BRIGHT}✗ {result['message']}{Style.RESET_ALL}{' ' * (58 - len(result['message']) - 2)}{Fore.RED}│{Style.RESET_ALL}")
                print(f"{Fore.RED}└{'─' * 58}┘{Style.RESET_ALL}")
            return
        
        if action == 'check_ollama':
            if self._check_ollama_server():
                self.ollama_running = True
                models = self._list_models()
                print(f"\n{Fore.GREEN}┌{'─' * 58}┐{Style.RESET_ALL}")
                print(f"{Fore.GREEN}│{Style.RESET_ALL} {Style.BRIGHT}✓ Ollama is running{Style.RESET_ALL}{' ' * 39}{Fore.GREEN}│{Style.RESET_ALL}")
                print(f"{Fore.GREEN}└{'─' * 58}┘{Style.RESET_ALL}")
                print(f"\n  URL: {self.ollama_url}")
                print(f"  Available models: {len(models)}")
                for model in models:
                    print(f"    • {model.get('name', 'unknown')}")
            else:
                self.ollama_running = False
                print(f"\n{Fore.RED}┌{'─' * 58}┐{Style.RESET_ALL}")
                print(f"{Fore.RED}│{Style.RESET_ALL} {Style.BRIGHT}✗ Ollama is not running{Style.RESET_ALL}{' ' * 34}{Fore.RED}│{Style.RESET_ALL}")
                print(f"{Fore.RED}└{'─' * 58}┘{Style.RESET_ALL}")
                print(f"\n  Try: {Fore.YELLOW}start ollama{Style.RESET_ALL}")
            return
        
        if action == 'list_models':
            models = self._list_models()
            if models:
                print(f"\n{Fore.CYAN}╔{'═' * 58}╗{Style.RESET_ALL}")
                print(f"{Fore.CYAN}║{Style.RESET_ALL} {Style.BRIGHT}Available Ollama Models{Style.RESET_ALL}{' ' * 30}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╠{'═' * 58}╣{Style.RESET_ALL}")
                for i, model in enumerate(models, 1):
                    print(f"{Fore.CYAN}║{Style.RESET_ALL}   {i}. {model.get('name', 'unknown'):<48}{Fore.CYAN}║{Style.RESET_ALL}")
                print(f"{Fore.CYAN}╚{'═' * 58}╝{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}┌{'─' * 58}┐{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}│{Style.RESET_ALL} {Style.BRIGHT}No models found. Pull one with: pull [model]{Style.RESET_ALL}{' ' * 4}{Fore.YELLOW}│{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}└{'─' * 58}┘{Style.RESET_ALL}")
            return
        
        if action == 'pull_model':
            model = parsed.get('model', '')
            if not model:
                print(f"\n{Fore.YELLOW}Usage: pull [model_name]{Style.RESET_ALL}")
                print("  Example: pull llama3.2")
                return
            result = self._pull_model(model)
            if result['success']:
                print(f"\n{Fore.GREEN}✓ {result['message']}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ {result['message']}{Style.RESET_ALL}")
            return
        
        if action == 'scan_projects':
            print(f"\n{Fore.CYAN}Scanning for projects...{Style.RESET_ALL}")
            home = Path.home()
            projects = []
            
            # Scan common locations
            scan_dirs = [home, home / 'projects', home / 'code', Path('/home/tbaltzakis')]
            
            for scan_dir in scan_dirs:
                if scan_dir.exists():
                    try:
                        for item in scan_dir.iterdir():
                            if item.is_dir():
                                # Check for project indicators
                                if (item / 'package.json').exists() or \
                                   (item / 'pyproject.toml').exists() or \
                                   (item / 'requirements.txt').exists() or \
                                   (item / 'Cargo.toml').exists() or \
                                   (item / '.git').exists():
                                    projects.append(item)
                    except PermissionError:
                        continue
            
            if projects:
                print(f"\n{Fore.GREEN}Found {len(projects)} project(s):{Style.RESET_ALL}")
                for i, project in enumerate(projects, 1):
                    # Detect type
                    if (project / 'package.json').exists():
                        ptype = 'Node.js'
                    elif (project / 'pyproject.toml').exists():
                        ptype = 'Python'
                    elif (project / 'Cargo.toml').exists():
                        ptype = 'Rust'
                    else:
                        ptype = 'Unknown'
                    
                    print(f"\n  {i}. {project.name}")
                    print(f"     Type: {ptype}")
                    print(f"     Path: {project}")
            else:
                print(f"\n{Fore.YELLOW}No projects found in scanned directories.{Style.RESET_ALL}")
            return
        
        if action == 'connect_project':
            path = parsed.get('path', '')
            if not path:
                print(f"\n{Fore.YELLOW}Usage: connect [path]{Style.RESET_ALL}")
                print("  Example: connect /home/user/my-project")
                return
            
            result = self._set_project(path)
            if result['success']:
                self.project_path = result['path']
                self.project_name = result['name']
                self.project_type = result['type']
                print(f"\n{Fore.GREEN}✓ {result['message']}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}✗ {result['message']}{Style.RESET_ALL}")
            return
        
        if action == 'test':
            return self._run_tests()
        
        if action == 'test_and_fix':
            return self._run_tests_and_fix()
        
        if action == 'build':
            return self._run_build()
        
        if action == 'research':
            return self._research(parsed.get('topic', ''))
        
        if action == 'search':
            return self._search(parsed.get('query', ''))
        
        if action == 'search_interactive':
            return self._search_web_interactive(parsed.get('query', ''))
        
        if action == 'docs':
            return self._get_docs(parsed.get('api', ''))
        
        if action == 'storm':
            return self._run_storm(parsed.get('command', ''))
        
        if action == 'design':
            return self._design(parsed.get('command', ''))
        
        if action == 'tdd':
            return self._run_tdd(parsed.get('command', ''))
        
        if action == 'analyze':
            return self._analyze(parsed.get('command', ''))
        
        if action == 'analyze_codebase':
            return self._analyze_codebase(parsed.get('command', ''))
        
        if action == 'generate_code':
            return self._generate_code(parsed.get('command', ''))
        
        if action == 'check_errors':
            return self._check_errors()
        
        if action == 'orchestrate':
            return self._orchestrate(parsed.get('command', ''))

        if action == 'ask':
            return self._launch_terminal_agent(parsed.get('command', ''))
    
    def _launch_terminal_agent(self, command):
        """Launch a terminal-separated agent session via ollama-agent.sh."""
        command = (command or '').strip()
        if not command:
            print(f"\n{Fore.YELLOW}Usage: ask [prompt]{Style.RESET_ALL}")
            print("Example: ask Write a Python function that returns the Fibonacci sequence")
            print("\n{Fore.GREEN} Launching terminal agent...{Style.RESET_ALL}")
            # Launch without prompt - interactive mode
            self._run_terminal_helper([])
            return

        # Strip "ask " or "chat " prefix
        stripped = command
        for prefix in ['ask ', 'chat ']:
            if stripped.lower().startswith(prefix):
                stripped = stripped[len(prefix):].strip()
                break

        print(f"\n{Fore.GREEN} Launching terminal agent with prompt...{Style.RESET_ALL}\n")
        # Launch with prompt
        self._run_terminal_helper([stripped])
    
    def _run_terminal_helper(self, args):
        """Run the terminal-separated agent helper script."""
        script_path = Path(__file__).parent / 'scripts' / 'ollama-agent-terminal.py'
        
        if not script_path.exists():
            print(f"\n{Fore.RED}✗ Terminal helper not found: {script_path}{Style.RESET_ALL}")
            return
        
        # Build the command
        cmd = [sys.executable, str(script_path)]
        
        # Add model and URL options
        cmd.extend(['--model', self.ollama_model])
        cmd.extend(['--url', self.ollama_url])
        
        # Add project path
        cmd.extend(['--project-path', self.project_path])
        
        # Add any user-provided args
        cmd.extend(args)
        
        try:
            # Run the terminal helper
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"\n{Fore.RED}✗ Terminal helper exited with error: {e}{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}✗ Error launching terminal helper: {e}{Style.RESET_ALL}")

    def _run_tests(self):
        """Run tests."""
        print(f"\n{Fore.CYAN}Running tests...{Style.RESET_ALL}\n")
        
        result = self.sandbox.execute("pnpm test")
        
        if result['success']:
            print(f"{Fore.GREEN}✓ All tests passed!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Tests failed{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Output:{Style.RESET_ALL}")
            print(result['stdout'][-1000:])
            if result.get('stderr'):
                print(result['stderr'][-500:])
    
    def _run_tests_and_fix(self):
        """Run tests and attempt to fix failures."""
        print(f"\n{Fore.CYAN}Running tests and analyzing failures...{Style.RESET_ALL}\n")
        
        result = self.sandbox.execute("pnpm test")
        
        if result['success']:
            print(f"{Fore.GREEN}✓ All tests passed!{Style.RESET_ALL}")
            return
        
        print(f"{Fore.RED}✗ Tests failed. Analyzing...{Style.RESET_ALL}\n")
        
        # Analyze the error
        diagnosis = self.debugger.analyze_error(
            result['stderr'] or result['stdout'],
            file_path=None
        )
        
        print(f"{Fore.YELLOW}Error Type:{Style.RESET_ALL} {diagnosis.get('error_type', 'Unknown')}")
        print(f"{Fore.YELLOW}Severity:{Style.RESET_ALL} {diagnosis.get('severity', 'Unknown')}")
        print(f"\n{Fore.CYAN}Root Cause:{Style.RESET_ALL}")
        print(diagnosis.get('root_cause', 'Unknown')[:500] if diagnosis.get('root_cause') else 'Unknown')
        
        print(f"\n{Fore.CYAN}Suggested Fix:{Style.RESET_ALL}")
        print(diagnosis.get('suggested_fix', 'Unknown')[:500])
    
    def _run_build(self):
        """Run build."""
        print(f"\n{Fore.CYAN}Running build...{Style.RESET_ALL}\n")
        
        result = self.sandbox.execute("pnpm build")
        
        if result['success']:
            print(f"{Fore.GREEN}✓ Build successful!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Build failed{Style.RESET_ALL}")
            print(f"\n{Fore.YELLOW}Output:{Style.RESET_ALL}")
            print(result['stderr'][-1000:] if result.get('stderr') else result['stdout'][-1000:])
    
    def _analyze_codebase(self, command):
        """Analyze the codebase with NLP-based intent."""
        print(f"\n{Fore.CYAN}Analyzing codebase...{Style.RESET_ALL}\n")
        
        # Use current project context automatically
        if self.project_path and self.project_path != os.getcwd():
            pass
        else:
            f"Current Directory: {os.getcwd()}"
        
        # Auto-detect the task based on NLP
        command_lower = command.lower()
        
        # Determine the analysis mode
        if 'error' in command_lower or 'bug' in command_lower or 'fix' in command_lower:
            mode = 'debug'
            task = f"Identify and fix issues in the codebase at {self.project_path}"
        elif 'security' in command_lower or 'vulnerability' in command_lower:
            mode = 'architect'
            task = f"Analyze security considerations for {self.project_name}"
        elif 'performance' in command_lower or 'optimize' in command_lower:
            mode = 'code'
            task = f"Review performance optimization opportunities in {self.project_name}"
        else:
            # Default: comprehensive code review
            mode = 'auto'
            task = f"Review the codebase at {self.project_path} and identify issues, improvements, and best practices"
        
        print(f"Mode: {mode}")
        print(f"Task: {task}\n")
        
        result = self.orchestrator.execute(
            task=task,
            mode=mode,
            context={
                'project_path': self.project_path,
                'project_name': self.project_name,
                'project_type': self.project_type,
            }
        )
        
        output = result.get('final_output', result.get('output', 'No output'))
        
        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Codebase Analysis Results:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(output[:3000])
        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def _research(self, topic):
        """Research a topic."""
        print(f"\n{Fore.CYAN}Researching: {topic}{Style.RESET_ALL}\n")
        
        research = self.web.research(topic, sources=3)
        
        print(f"{Fore.YELLOW}Sources:{Style.RESET_ALL}")
        for source in research['sources_used']:
            print(f"  - {source['title']}: {source['url']}")
        
        print(f"\n{Fore.YELLOW}Key Findings:{Style.RESET_ALL}")
        for i, finding in enumerate(research['key_findings'][:5], 1):
            print(f"  {i}. {finding[:150]}...")
        
        print(f"\n{Fore.YELLOW}Full Summaries:{Style.RESET_ALL}")
        for summary in research['summaries']:
            print(f"\n  [{summary['source']}]")
            print(f"  URL: {summary['url']}")
            print(f"  Summary: {summary['summary'][:300]}...")
    
    def _generate_code(self, command):
        """Generate code automatically based on NLP command."""
        print(f"\n{Fore.CYAN}Generating code...{Style.RESET_ALL}\n")
        
        # Extract the feature/component from the command
        command_lower = command.lower()
        
        # Determine what to generate
        if 'api' in command_lower or 'endpoint' in command_lower:
            component = 'API endpoint'
        elif 'component' in command_lower or 'module' in command_lower:
            component = 'component'
        elif 'function' in command_lower or 'utility' in command_lower:
            component = 'function'
        elif 'test' in command_lower:
            component = 'test'
        else:
            component = 'code'
        
        # Use current project context automatically
        context = {
            'project_path': self.project_path,
            'project_name': self.project_name,
            'project_type': self.project_type,
            'component': component,
        }
        
        print(f"Generating: {component}")
        print(f"Project: {self.project_name}\n")
        
        result = self.orchestrator.execute(
            task=f"Generate {component} for: {command}",
            mode='code',
            context=context
        )
        
        output = result.get('final_output', result.get('output', 'No output'))
        
        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Generated Code:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(output[:4000])
        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def _search(self, query):
        """Search the web."""
        print(f"\n{Fore.CYAN}Searching: {query}{Style.RESET_ALL}\n")
        
        results = self.web.search(query, max_results=5)
        
        for i, result in enumerate(results, 1):
            print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {result['title']}")
            print(f"   {result['url']}")
            print(f"   {result['snippet'][:100]}...\n")
    
    def _search_web_interactive(self, query):
        """Interactive web search with URL selection."""
        print(f"\n{Fore.CYAN}Searching: {query}{Style.RESET_ALL}\n")
        
        results = self.web.search(query, max_results=10)
        
        if not results:
            print(f"{Fore.RED}No results found.{Style.RESET_ALL}")
            return
        
        print(f"{Fore.YELLOW}Select a URL to fetch (1-{len(results)}):{Style.RESET_ALL}")
        for i, result in enumerate(results, 1):
            print(f"  {Fore.CYAN}{i}.{Style.RESET_ALL} {result['title']}")
            print(f"     {result['url']}")
        
        try:
            selection = input(f"\n{Fore.GREEN}Enter number (or 'all' for all):{Style.RESET_ALL} ").strip()
            
            if selection.lower() == 'all':
                print(f"\n{Fore.CYAN}Fetching all results...{Style.RESET_ALL}\n")
                for result in results:
                    fetch_result = self.web.fetch(result['url'], max_length=3000)
                    if fetch_result['success']:
                        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
                        print(f"{Fore.GREEN}Source: {result['title']}{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}URL: {result['url']}{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}Content preview:{Style.RESET_ALL}")
                        print(fetch_result['content'][:1000] + "..." if len(fetch_result['content']) > 1000 else "")
                        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
            else:
                idx = int(selection) - 1
                if 0 <= idx < len(results):
                    result = results[idx]
                    print(f"\n{Fore.CYAN}Fetching: {result['title']}{Style.RESET_ALL}\n")
                    fetch_result = self.web.fetch(result['url'], max_length=5000)
                    if fetch_result['success']:
                        print(f"{Fore.WHITE}URL: {result['url']}{Style.RESET_ALL}")
                        print(f"{Fore.WHITE}Content:{Style.RESET_ALL}")
                        print(fetch_result['content'][:2000] + "..." if len(fetch_result['content']) > 2000 else "")
                else:
                    print(f"{Fore.RED}Invalid selection.{Style.RESET_ALL}")
        except (ValueError, KeyboardInterrupt):
            print(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
    
    def _get_docs(self, api):
        """Get API documentation."""
        print(f"\n{Fore.CYAN}Fetching documentation for: {api}{Style.RESET_ALL}\n")
        
        docs = self.web.get_api_docs(api)
        
        if docs['success']:
            print(docs['content'][:2000])
        else:
            print(f"{Fore.RED}Could not fetch documentation{Style.RESET_ALL}")
    
    def _run_storm(self, command):
        """Run Agent Storm."""
        print(f"\n{Fore.CYAN}Running Agent Storm...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Task:{Style.RESET_ALL} {command}\n")
        
        result = self.storm.storm(
            task=command,
            prompt="Provide comprehensive analysis and solution",
            num_agents=4,
        )
        
        print(f"{Fore.GREEN}Completed in {result['duration_seconds']:.1f}s{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Synthesized Solution:{Style.RESET_ALL}\n")
        print(result['synthesis']['synthesis'][:2000])
        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def _design(self, command):
        """Design with multiple perspectives."""
        print(f"\n{Fore.CYAN}Designing with multiple perspectives...{Style.RESET_ALL}\n")
        
        result = self.storm.storm_with_roles(
            task=command,
            prompt="Consider architecture, security, and implementation",
            roles=["architect", "security", "backend"],
        )
        
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(result['synthesis']['synthesis'][:2000])
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def _run_tdd(self, command):
        """Run TDD workflow."""
        print(f"\n{Fore.CYAN}Starting TDD workflow...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Task:{Style.RESET_ALL} {command}\n")
        print(f"{Fore.YELLOW}Note:{Style.RESET_ALL} TDD requires specific file paths.")
        print("Use format: 'implement [feature] in [file] with tests in [test_file]'\n")
        
        # For now, use orchestrator in code mode
        result = self.orchestrator.execute(
            task=command,
            mode="code"
        )
        
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(result['output'][:2000])
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def _analyze(self, command):
        """Analyze code."""
        print(f"\n{Fore.CYAN}Analyzing...{Style.RESET_ALL}\n")
        
        result = self.orchestrator.execute(
            task=command,
            mode="debug"
        )
        
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(result['output'][:2000])
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def _check_errors(self):
        """Check for errors in the project."""
        print(f"\n{Fore.CYAN}Checking for errors...{Style.RESET_ALL}\n")
        
        # Run type check or lint
        result = self.sandbox.execute("pnpm lint 2>&1 || pnpm typecheck 2>&1 || echo 'No lint/typecheck available'")
        
        if result['success']:
            print(f"{Fore.GREEN}✓ No errors found{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Issues found:{Style.RESET_ALL}")
            print(result['stdout'][-1500:])
    
    def _orchestrate(self, command):
        """Use orchestrator for general tasks."""
        print(f"\n{Fore.CYAN}Processing request...{Style.RESET_ALL}\n")
        
        result = self.orchestrator.execute(
            task=command,
            mode="auto"
        )
        
        output = result.get('final_output', result.get('output', 'No output'))
        
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(output[:3000])
        print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
    
    def run(self):
        """Run the main GUI loop."""
        self.clear_screen()
        self.print_header()
        print(f"{Fore.YELLOW}Type 'help' for available commands{Style.RESET_ALL}")
        print()
        
        while self.running:
            try:
                # Get user input
                command = input(f"{Fore.GREEN}You:{Style.RESET_ALL} ").strip()
                
                if not command:
                    continue
                
                # Store in history
                self.history.append({'command': command})
                
                # Parse and execute
                parsed = self.parse_command(command)
                self.execute_action(parsed)
                
                print()
                
            except KeyboardInterrupt:
                print(f"\n\n{Fore.YELLOW}Interrupted. Type 'exit' to quit.{Style.RESET_ALL}\n")
            except EOFError:
                print(f"\n{Fore.YELLOW}Goodbye!{Style.RESET_ALL}\n")
                break
            except Exception as e:
                print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}\n")


def main():
    """Main entry point."""
    gui = AgentGUI()
    gui.run()


if __name__ == "__main__":
    main()
