#!/usr/bin/env python3
"""Test the NLP processor."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.nlp_processor import NLPProcessor

def test_basic_parsing():
    """Test basic intent parsing."""
    processor = NLPProcessor()
    
    tests = [
        ("analyze codebase", "analyze"),
        ("create API endpoint", "code"),
        ("run tests", "test"),
        ("research Next.js", "unknown"),  # Default fallback
    ]
    
    print("Testing NLP Processor...\n")
    passed = 0
    
    for command, expected in tests:
        result = processor.parse(command)
        if result.intent.value == expected:
            print(f"✓ '{command}' -> {result.intent.value} (confidence: {result.confidence:.2f})")
            passed += 1
        else:
            print(f"✗ '{command}' -> {result.intent.value} (expected: {expected})")
    
    print(f"\n{passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    if test_basic_parsing():
        print("\n✓ NLP processor is ready!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)