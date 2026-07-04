#!/bin/bash
# Start Ollama server and models

echo "Starting Ollama server..."

# Check if Ollama is already running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama server is already running"
    echo "Available models:"
    curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  - {m[\"name\"]}') for m in d.get('models',[])]"
    exit 0
fi

# Try to start Ollama service
if command -v systemctl &> /dev/null; then
    echo "Attempting to start Ollama service..."
    if sudo -n systemctl start ollama 2>/dev/null; then
        echo "✓ Ollama service started"
    else
        echo "Trying ollama serve in background..."
        ollama serve &
        OLLAMA_PID=$!
        echo "Ollama started with PID: $OLLAMA_PID"
    fi
else
    echo "Starting Ollama server directly..."
    ollama serve &
    OLLAMA_PID=$!
    echo "Ollama started with PID: $OLLAMA_PID"
fi

# Wait for server to be ready
echo "Waiting for Ollama to start..."
sleep 5

# Verify server is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✓ Ollama server is running"
    echo "Available models:"
    curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'  - {m[\"name\"]}') for m in d.get('models',[])]"
else
    echo "✗ Ollama server failed to start"
    exit 1
fi
