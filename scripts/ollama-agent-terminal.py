#!/usr/bin/env python3
"""
DeepAgents + Ollama Terminal Helper
====================================

A terminal-separated agent execution helper that runs in its own terminal window.
This script is launched by GUI or OS launchers to provide isolated agent sessions.

Features:
- Terminal-separated execution with proper TTY handling
- Interactive REPL mode
- One-shot prompt execution
- Environment variable support (OLLAMA_URL, OLLAMA_MODEL, PROJECT_PATH)

Usage:
    # From GUI/launcher (interactive)
    python scripts/ollama-agent-terminal.py

    # One-shot execution
    python scripts/ollama-agent-terminal.py "Your prompt here"

    # With options
    python scripts/ollama-agent-terminal.py --model llama3.1 --url http://localhost:11434 "Your prompt"

    # Interactive mode explicitly
    python scripts/ollama-agent-terminal.py --interactive
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations import create_ollama_agent


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="DeepAgents + Ollama Terminal Helper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python ollama-agent-terminal.py
  python ollama-agent-terminal.py "Write a Python function"
  python ollama-agent-terminal.py --interactive
  python ollama-agent-terminal.py --model qwen2.5-coder "Your prompt"
        """
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="One-shot prompt to execute (optional)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Force interactive REPL mode"
    )
    
    parser.add_argument(
        "-m", "--model",
        default=os.environ.get("OLLAMA_MODEL", "qwen2.5-coder"),
        help="Ollama model name (default: OLLAMA_MODEL env or qwen2.5-coder)"
    )
    
    parser.add_argument(
        "-u", "--url",
        default=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        help="Ollama server URL (default: OLLAMA_URL env or http://localhost:11434)"
    )
    
    parser.add_argument(
        "-p", "--project-path",
        default=os.environ.get("PROJECT_PATH", os.getcwd()),
        help="Project path for context (default: PROJECT_PATH env or current dir)"
    )
    
    return parser.parse_args()


def run_one_shot(agent, prompt: str) -> None:
    """Execute a single prompt and exit."""
    print(f"\n{'=' * 60}")
    print(f"Prompt: {prompt}")
    print(f"{'=' * 60}\n")
    
    try:
        result = agent.invoke({"messages": prompt})
        output = result.get("messages", result)
        
        if isinstance(output, list):
            for msg in output:
                if hasattr(msg, "content"):
                    print(msg.content)
                elif isinstance(msg, dict):
                    print(msg.get("content", msg))
                else:
                    print(msg)
        else:
            print(output)
        
        print(f"\n{'=' * 60}")
        print("Done.")
        print(f"{'=' * 60}")
        
    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"Error: {e}")
        print(f"{'=' * 60}")
        sys.exit(1)


def run_interactive(agent, model: str, project_path: str) -> None:
    """Run interactive REPL mode."""
    print()
    print(f"{'=' * 60}")
    print("DeepAgents + Ollama Terminal Helper")
    print(f"{'=' * 60}")
    print(f"Model: {model}")
    print(f"URL: {agent.llm_model.base_url if hasattr(agent, 'llm_model') else 'N/A'}")
    print(f"Project: {project_path}")
    print(f"{'=' * 60}")
    print()
    print("Type your prompt and press Enter.")
    print("Commands:")
    print("  /exit, /quit  - Exit terminal helper")
    print("  /clear        - Clear screen")
    print("  /help         - Show this help")
    print()
    
    # Clear screen
    os.system("clear" if os.name == "posix" else "cls")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.startswith("/"):
                command = user_input[1:].lower()
                
                if command in ["exit", "quit"]:
                    print("\nGoodbye!")
                    break
                
                if command == "clear":
                    os.system("clear" if os.name == "posix" else "cls")
                    print("DeepAgents + Ollama Terminal Helper")
                    print(f"Model: {model}")
                    print(f"Project: {project_path}")
                    print("Type /exit or /quit to leave.")
                    print()
                    continue
                
                if command == "help":
                    print()
                    print("Commands:")
                    print("  /exit, /quit  - Exit terminal helper")
                    print("  /clear        - Clear screen")
                    print("  /help         - Show this help")
                    print()
                    continue
            
            # Execute prompt
            result = agent.invoke({"messages": user_input})
            output = result.get("messages", result)
            
            print()
            if isinstance(output, list):
                for msg in output:
                    if hasattr(msg, "content"):
                        print(msg.content)
                    elif isinstance(msg, dict):
                        print(msg.get("content", msg))
                    else:
                        print(msg)
            else:
                print(output)
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type /exit or /quit to quit.")
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print()


def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Determine mode
    interactive_mode = args.interactive or (args.prompt is None)
    
    # Create agent
    agent = create_ollama_agent(
        model=args.model,
        base_url=args.url,
    )
    
    # Add model reference to agent for display
    agent.ollama_model = args.model
    agent.ollama_url = args.url
    agent.project_path = args.project_path
    
    if interactive_mode:
        run_interactive(agent, args.model, args.project_path)
    else:
        run_one_shot(agent, args.prompt)


if __name__ == "__main__":
    main()
