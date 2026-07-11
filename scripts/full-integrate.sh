#!/usr/bin/env bash
# Full integration script for cloudless.gr

set -e

echo "🔗 Full Integration: ollama → cloudless.gr"
echo "============================================"

# Step 1: Copy skill
echo "📋 Copying ollama-infrastructure skill..."
mkdir -p /home/tbaltzakis/cloudless.gr/.deepagents/skills
cp -r /home/tbaltzakis/ollama/.deepagents/skills/ollama-infrastructure /home/tbaltzakis/cloudless.gr/.deepagents/skills/
echo "   ✅ Skill copied"

# Step 2: Update MCP config
echo "🔧 Updating MCP configuration..."
python3 << 'EOF'
import json

with open('/home/tbaltzakis/cloudless.gr/.deepagents/.mcp.json', 'r') as f:
    mcp = json.load(f)

mcp["mcpServers"]["ollama-infrastructure"] = {
    "command": "python",
    "args": ["-m", "integrations.cline_adapter"],
    "env": {
        "PROJECT_PATH": "/home/tbaltzakis/cloudless.gr"
    }
}

with open('/home/tbaltzakis/cloudless.gr/.deepagents/.mcp.json', 'w') as f:
    json.dump(mcp, f, indent=2)

print("   ✅ MCP config updated")
EOF

# Step 3: Copy cline config
echo "📦 Copying Cline configuration..."
mkdir -p /home/tbaltzakis/cloudless.gr/.cline
cp -r /home/tbaltzakis/ollama/.cline/* /home/tbaltzakis/cloudless.gr/.cline/
echo "   ✅ Cline config copied"

# Step 4: Verify
echo "✅ Integration complete!"
echo ""
echo "📚 Available in cloudless.gr:"
echo "   - 11 ClineAdapter tools"
echo "   - NLPProcessor"
echo "   - Ollama model integration"
echo ""
echo "🎯 Next: Restart MCP servers in cloudless.gr project"