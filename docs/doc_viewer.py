#!/usr/bin/env python3
"""
Documentation Viewer GUI
========================

A terminal-based GUI for browsing project documentation with fuzzy search.

Usage:
    python3 docs/doc_viewer.py
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

# Try to import colorama for cross-platform colors
try:
    from colorama import init, Fore, Style
    init()
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'
        DIM = '\033[2m'
        RESET_ALL = '\033[0m'


class DocViewer:
    """Documentation browser with fuzzy search."""

    def __init__(self, docs_dir: str = "docs"):
        self.docs_dir = Path(docs_dir)
        self.documents: List[Dict[str, str]] = []
        self._load_documents()

    def _load_documents(self) -> None:
        """Load all markdown documents."""
        if not self.docs_dir.exists():
            self.docs_dir = Path(__file__).parent
        
        for md_file in sorted(self.docs_dir.glob("*.md")):
            self.documents.append({
                "name": md_file.stem.replace("_", " ").title(),
                "filename": md_file.name,
                "path": str(md_file),
            })

    def clear_screen(self) -> None:
        """Clear the terminal."""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self) -> None:
        """Print header."""
        print()
        print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}Documentation Viewer{Style.RESET_ALL}{' ' * 37}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        print()

    def print_documents(self, filter_text: str = "") -> None:
        """Print list of available documents."""
        print(f"{Fore.YELLOW}Available Documents:{Style.RESET_ALL}\n")
        
        for i, doc in enumerate(self.documents, 1):
            name = doc["name"]
            if filter_text.lower() in name.lower():
                print(f"  {Fore.CYAN}{i}.{Style.RESET_ALL} {name}")
                print(f"       {Fore.WHITE}{doc['filename']}{Style.RESET_ALL}")

    def view_document(self, filename: str) -> None:
        """View a specific document."""
        doc_path = self.docs_dir / filename
        if not doc_path.exists():
            print(f"{Fore.RED}File not found: {filename}{Style.RESET_ALL}")
            return

        self.clear_screen()
        print(f"{Fore.CYAN}╔{'═' * 60}╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL} {Fore.WHITE}{Style.BRIGHT}{filename}{Style.RESET_ALL}{' ' * (56 - len(filename))}{Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚{'═' * 60}╝{Style.RESET_ALL}")
        print()

        content = doc_path.read_text()
        # Print first 100 lines with pagination hint
        lines = content.split('\n')
        for line in lines[:100]:
            # Highlight headers
            if line.startswith('#'):
                print(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
            elif line.startswith('##'):
                print(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
            else:
                print(line)

        if len(lines) > 100:
            print(f"\n{Fore.YELLOW}... ({len(lines) - 100} more lines){Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
        print(f"Commands: {Fore.GREEN}r{Style.RESET_ALL}=return to menu, {Fore.GREEN}q{Style.RESET_ALL}=quit")
        cmd = input(f"{Fore.WHITE}> {Style.RESET_ALL}").strip().lower()

    def run(self) -> None:
        """Run the documentation viewer."""
        while True:
            self.clear_screen()
            self.print_header()
            self.print_documents()
            
            print(f"\n{Fore.YELLOW}Enter document number or 'q' to quit:{Style.RESET_ALL}")
            choice = input(f"{Fore.WHITE}> {Style.RESET_ALL}").strip()

            if choice.lower() == 'q':
                break
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.documents):
                    self.view_document(self.documents[idx]["filename"])
                    # After view, check for return/quit
                    while True:
                        cmd = input(f"{Fore.WHITE}> {Style.RESET_ALL}").strip().lower()
                        if cmd in ('q', 'quit', 'exit'):
                            return
                        elif cmd in ('r', 'return', ''):
                            break
            except ValueError:
                pass


if __name__ == "__main__":
    viewer = DocViewer()
    viewer.run()