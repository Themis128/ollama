#!/usr/bin/env bash
set -euo pipefail

OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434/v1}"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3.2}"

echo "==> Ollama base URL: $OLLAMA_BASE_URL"
echo "==> Ollama model:    $OLLAMA_MODEL"

curl -sS "$OLLAMA_BASE_URL/chat/completions" \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$OLLAMA_MODEL\",
    \"messages\": [
      {
        \"role\": \"system\",
        \"content\": \"You are a concise local test assistant.\"
      },
      {
        \"role\": \"user\",
        \"content\": \"Say hello from Ollama OpenAI-compatible endpoint.\"
      }
    ],
    \"stream\": false
  }" | python3 -m json.tool
