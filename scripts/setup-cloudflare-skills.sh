#!/bin/bash
# Setup Cloudflare skills for DeepAgents + Ollama projects
# Clones the Cloudflare skills repo into .deepagents/skills/cloudflare

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

TARGET_DIR=".deepagents/skills/cloudflare"
REPO_URL="https://github.com/cloudflare/skills.git"

# Clone or update Cloudflare skills
if [ ! -d "$TARGET_DIR/.git" ]; then
    echo -e "${BLUE}Cloning Cloudflare skills repo...${NC}"
    mkdir -p .deepagents/skills
    git clone "$REPO_URL" "$TARGET_DIR"
    echo -e "${GREEN}✓ Cloudflare skills installed to $TARGET_DIR${NC}"
else
    echo -e "${BLUE}Updating existing Cloudflare skills...${NC}"
    git -C "$TARGET_DIR" pull --ff-only
    echo -e "${GREEN}✓ Cloudflare skills updated${NC}"
fi

echo ""
echo "Next steps:"
echo "  - Review skills under: .deepagents/skills/cloudflare"
echo "  - Add Cloudflare MCP servers to .deepagents/.mcp.json"
echo "  - See docs/CLOUDFLARE_SKILLS.md for MCP config examples"
