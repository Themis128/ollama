#!/bin/bash
# Stop Ollama server

echo "Stopping Ollama server..."

# Try systemctl first, fall back to pkill
if command -v systemctl &> /dev/null && systemctl is-active --quiet ollama 2>/dev/null; then
    sudo -n systemctl stop ollama 2>/dev/null || pkill -f 'ollama serve' 2>/dev/null || true
else
    pkill -f 'ollama serve' 2>/dev/null || true
fi

sleep 2

# Verify server is stopped
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✗ Ollama server is still running"
    exit 1
else
    echo "✓ Ollama server has stopped"
fi
