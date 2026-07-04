#!/bin/bash
# Test DeepAgents + Ollama agent

echo "Testing DeepAgents + Ollama agent..."

# Navigate to scripts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
source .venv/bin/activate

# Run the test
python3 -c "
import sys
sys.path.insert(0, '/home/tbaltzakis/ollama')

from integrations.deepagents_ollama import create_ollama_agent

print('='*60)
print('DEEPAGENTS + OLLAMA INTEGRATION TEST')
print('='*60)

agent = create_ollama_agent(
    model='qwen2.5-coder',
    base_url='http://localhost:11434',
)

# Test simple task
result = agent.invoke({
    'messages': [
        ('human', 'Write a Python function to calculate Fibonacci numbers.')
    ]
})

print()
print('OUTPUT:')
print(result['messages'][-1].content)
print()
print('='*60)
print('TEST PASSED!')
print('='*60)
"
