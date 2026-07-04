#!/bin/bash
# Start DeepAgents + Ollama agent

echo "Starting DeepAgents + Ollama agent..."

# Navigate to scripts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
source .venv/bin/activate

# Run the test or start the agent
python3 integrations/deepagents_ollama.py
