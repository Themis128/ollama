#!/bin/bash
# Stop Ollama server

echo "Stopping Ollama server..."

# Stop Ollama service
sudo systemctl stop ollama

# Verify server is stopped
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✗ Ollama server is still running"
    exit 1
else
    echo "✓ Ollama server has stopped"
fi
