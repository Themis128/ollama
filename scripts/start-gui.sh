#!/bin/bash
# Start DeepAgents + Ollama GUI with preload of new implementations

echo "Starting DeepAgents + Ollama GUI..."

# Navigate to scripts directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment
source .venv/bin/activate

# Preload new implementations
echo "Preloading new implementations..."
python3 -c "
import sys
sys.path.insert(0, '.')
from integrations import (
    TDDAgent,
    TerminalAgent,
    SandboxAgent,
    Orchestrator,
    WebAgent,
    DebugAgent,
    AgentStorm,
)
print('✓ All new implementations preloaded successfully')
"

# Run the GUI
python3 gui.py
