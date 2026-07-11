#!/usr/bin/env bash
# Debug Ollama server and connection

echo "🔍 Ollama Debug Information"
echo "============================"

# Check if Ollama is running
echo "📡 Server Status:"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama is running on http://localhost:11434"
else
    echo "   ❌ Ollama not responding - start with: ollama serve"
    exit 1
fi

# Show server info
echo ""
echo "📦 Available Models:"
curl -s http://localhost:11434/api/tags | python3 -c "
import json, sys
data = json.load(sys.stdin)
for m in data.get('models', []):
    print(f'   - {m[\"name\"]} ({m[\"size\"]/(1024**3):.1f} GB)')
"

# Show server health
echo ""
echo "❤️ Server Health:"
curl -s http://localhost:11434/api/version | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f'   Version: {data.get(\"version\", \"unknown\")}')
"

# Test ClineAdapter connection
echo ""
echo "🔌 ClineAdapter Test:"
python3 -c "
from integrations import ClineAdapter
adapter = ClineAdapter('/home/tbaltzakis/cloudless.gr')
result = adapter.run_tool('check_ollama', {})
if result['success']:
    print(f'   ✅ Connection successful')
    print(f'   Status: {result[\"status\"]}')
else:
    print(f'   ❌ Connection failed: {result.get(\"error\", \"unknown\")}')
"

# Show integration status
echo ""
echo "📚 Integration Status:"
if [ -d "/home/tbaltzakis/cloudless.gr/.deepagents/skills/ollama-infrastructure" ]; then
    echo "   ✅ cloudless.gr has ollama infrastructure"
else
    echo "   ❌ cloudless.gr missing infrastructure - run: ./scripts/full-integrate.sh"
fi

echo ""
echo "✅ Debug complete!"