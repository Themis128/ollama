#!/bin/bash
# Run agent tests

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

exec python3 -m pytest tests/ -v "$@"
