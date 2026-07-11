#!/usr/bin/env bash
# Continuous live logging for Ollama

LOG_FILE="/tmp/ollama-debug.log"

echo "📡 Live Ollama Debug Logs"
echo "Press Ctrl+C to stop"
echo "============================"
echo ""

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check server
    STATUS=$(curl -s http://localhost:11434/api/tags > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Down")
    
    # Get model count
    MODEL_COUNT=$(curl -s http://localhost:11434/api/tags | python3 -c "import json,sys; print(len(json.load(sys.stdin).get('models',[])))" 2>/dev/null || echo "0")
    
    echo "[$TIMESTAMP] Server: $STATUS | Models: $MODEL_COUNT" >> "$LOG_FILE"
    echo "[$TIMESTAMP] Server: $STATUS | Models: $MODEL_COUNT"
    
    sleep 5
done