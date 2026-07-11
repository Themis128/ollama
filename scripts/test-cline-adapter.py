#!/usr/bin/env python3
"""
Test Cline Adapter
===================

Quick test to verify the Cline adapter works with the ollama project.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.cline_adapter import ClineAdapter

def test_list_files():
    """Test listing files."""
    adapter = ClineAdapter(project_path="/home/tbaltzakis/cloudless.gr")
    result = adapter.run_tool("list_files", {"path": "/home/tbaltzakis/cloudless.gr", "max_depth": 2})
    
    if result["success"]:
        print("✓ List files works")
        print(f"  Found {len(result['files'])} files")
        return True
    else:
        print(f"✗ List files failed: {result['error']}")
        return False

def test_read_file():
    """Test reading a file."""
    adapter = ClineAdapter()
    result = adapter.run_tool("read_file", {"path": "/home/tbaltzakis/cloudless.gr/package.json"})
    
    if result["success"]:
        print("✓ Read file works")
        print(f"  File has {result['lines']} lines")
        return True
    else:
        print(f"✗ Read file failed: {result['error']}")
        return False

def test_check_ollama():
    """Test Ollama check."""
    adapter = ClineAdapter()
    result = adapter.run_tool("check_ollama", {})
    
    if result["success"]:
        print("✓ Ollama check works")
        print(f"  Status: {result['status']}")
        return True
    else:
        print(f"⚠ Ollama not running (expected): {result['status']}")
        return True  # Not a failure for this test

if __name__ == "__main__":
    print("Testing Cline Adapter...\n")
    
    results = [
        test_list_files(),
        test_read_file(),
        test_check_ollama(),
    ]
    
    print(f"\n{'='*50}")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ Cline adapter is ready!")
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        sys.exit(1)