#!/bin/bash
# Start the DeepAgents + Ollama agent (interactive mode)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

exec python3 scripts/ollama-agent-terminal.py --interactive "$@"
