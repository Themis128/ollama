#!/bin/bash
# Test the DeepAgents agent with a selected project

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Source project environment if exists
if [ -f "$SCRIPT_DIR/.project_env" ]; then
    source "$SCRIPT_DIR/.project_env"
    echo "Using project: $PROJECT_NAME"
    echo "Path: $PROJECT_PATH"
    echo ""
    cd "$PROJECT_PATH"
else
    # Default to cloudless.gr
    echo "No project selected. Using default: cloudless.gr"
    PROJECT_PATH="/home/tbaltzakis/cloudless.gr"
    cd "$PROJECT_PATH"
fi

# Check if project has DeepAgents setup
if [ ! -f "$PROJECT_PATH/.deepagents/AGENTS.md" ] && [ ! -f "$PROJECT_PATH/setup-deep-agents-env.sh" ]; then
    echo -e "${RED}Error: This project doesn't have a DeepAgents setup${NC}"
    echo ""
    echo "Required files missing:"
    echo "  - .deepagents/AGENTS.md"
    echo "  - setup-deep-agents-env.sh"
    echo ""
    echo "This may not be a DeepAgents-enabled project."
    exit 1
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Testing DeepAgents with: $PROJECT_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if dcode is available
if ! command -v dcode &> /dev/null; then
    echo "DeepAgents CLI (dcode) not found. Trying to source environment..."
    if [ -f "$PROJECT_PATH/setup-deep-agents-env.sh" ]; then
        source "$PROJECT_PATH/setup-deep-agents-env.sh"
    fi
fi

# Test basic agent
echo "Testing agent with a simple query..."
echo ""

# Check if dcode requires --model flag
if ! dcode --help 2>&1 | grep -q "interactive thread"; then
    echo "dcode is not the expected version"
    exit 1
fi

echo -e "${GREEN}✓ DeepAgents CLI is available${NC}"
echo ""
echo "You can now:"
echo "  - Start interactive mode: dcode"
echo "  - Use skills: dcode --skill <name> <query>"
echo "  - Use agents: dcode --agent <name> <query>"
echo ""
echo "Examples:"
echo "  dcode --skill code-review \"Review the auth module\""
echo "  dcode --skill deploy \"What's the deployment checklist?\""
echo "  dcode --agent backend-dev \"Explain the Stripe webhook flow\""
echo ""
echo "To start interactive mode:"
echo "  cd $PROJECT_PATH"
echo "  dcode"
echo ""

# Show available skills
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Available Skills"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
dcode skills list 2>/dev/null || echo "Skills command requires interactive mode"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Test Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
