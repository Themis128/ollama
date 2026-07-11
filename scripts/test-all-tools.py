#!/usr/bin/env python3
"""Test all ClineAdapter tools."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.cline_adapter import ClineAdapter

def main():
    adapter = ClineAdapter("/home/tbaltzakis/cloudless.gr")
    
    print("Testing All ClineAdapter Tools...")
    print("=" * 50)
    
    tests = [
        ("list_files", {"max_depth": 2}),
        ("read_file", {"path": "/home/tbaltzakis/cloudless.gr/package.json"}),
        ("search_files", {"pattern": "*.ts", "directory": "/home/tbaltzakis/cloudless.gr"}),
        ("get_file_info", {"path": "/home/tbaltzakis/cloudless.gr/package.json"}),
        ("analyze_code", {"focus": "structure"}),
        ("check_ollama", {}),
    ]
    
    passed = 0
    for tool, params in tests:
        result = adapter.run_tool(tool, params)
        status = "✓" if result["success"] else "✗"
        print(f"{status} {tool}")
        if result["success"]:
            passed += 1
        else:
            print(f"  Error: {result.get('error', 'Unknown')}")
    
    print(f"\n{'=' * 50}")
    print(f"Tools passed: {passed}/{len(tests)}")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)