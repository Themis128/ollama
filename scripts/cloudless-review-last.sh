#!/usr/bin/env bash
set -euo pipefail

export OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5-coder:latest}"

exec /home/tbaltzakis/ollama/scripts/review-cloudflare-result-with-ollama.py
