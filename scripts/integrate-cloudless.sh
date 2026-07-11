#!/usr/bin/env bash
# Integrate ollama infrastructure into cloudless.gr project

echo "🔗 Integrating ollama infrastructure into cloudless.gr..."

# Copy ollama skill to cloudless.gr
cp -r /home/tbaltzakis/ollama/.deepagents/skills/ollama-infrastructure /home/tbaltzakis/cloudless.gr/.deepagents/skills/

echo "✅ Skill copied to cloudless.gr/.deepagents/skills/ollama-infrastructure/"

echo "🎯 Manual step required:"
echo "Edit /home/tbaltzakis/cloudless.gr/.deepagents/.mcp.json"
echo "Add this to mcpServers:"
echo '  "ollama-infrastructure": {
    "command": "python",
    "args": ["-m", "integrations.cline_adapter"],
    "env": {
      "PROJECT_PATH": "/home/tbaltzakis/cloudless.gr"
    }
  }'
echo "✅ Integration instructions complete!"