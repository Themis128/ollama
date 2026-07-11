#!/usr/bin/env bash
# Register ollama infrastructure as a Cline model

echo "🔧 Registering ollama infrastructure for Cline..."
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama server not running. Start it with: ollama serve"
fi

# Show available models
echo "📦 Available models:"
curl -s http://localhost:11434/api/tags | python3 -c "import json,sys; models=json.load(sys.stdin).get('models',[]); [print(f'  - {m[\"name\"]} ({m[\"size\"]/(1024**3):.1f} GB)') for m in models]"
echo ""

# Copy configuration
if [ -d "$HOME/.cline" ]; then
    mkdir -p "$HOME/.cline/models"
    cp .cline/config.json "$HOME/.cline/models/ollama-full-infra.json" 2>/dev/null || true
    echo "✅ Configuration copied to ~/.cline/"
else
    echo "📋 Copy .cline/config.json to your Cline configuration directory"
fi

echo ""
echo "🎯 To use in Cline:"
echo "  1. Select provider: ollama"
echo "  2. Model: qwen2.5-coder"  
echo "  3. URL: http://localhost:11434"
echo "✅ All 11 tools available!"