#!/bin/bash
# Run a DeepAgents + Ollama agent session from the command line.
#
# Supports one-shot prompts and an interactive REPL.
#
# Usage:
#   ./scripts/ollama-agent.sh
#   ./scripts/ollama-agent.sh "Your prompt here"
#   ./scripts/ollama-agent.sh --interactive
#   ./scripts/ollama-agent.sh --model llama3.1 --base-url http://localhost:11434

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Activate virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

MODEL="${OLLAMA_MODEL:-qwen2.5-coder}"
BASE_URL="${OLLAMA_URL:-http://localhost:11434}"
PROJECT_PATH="${PROJECT_PATH:-$(pwd)}"
INTERACTIVE=false
PROMPT_INPUT=""

while [ $# -gt 0 ]; do
    case "$1" in
        --interactive|-i)
            INTERACTIVE=true
            shift
            ;;
        --model|-m)
            MODEL="$2"
            shift 2
            ;;
        --base-url|-u)
            BASE_URL="$2"
            shift 2
            ;;
        --project-path|-p)
            PROJECT_PATH="$2"
            shift 2
            ;;
        --help|-h)
            cat <<'USAGE'
Usage: ollama-agent.sh [OPTIONS] [PROMPT]

Options:
  -i, --interactive    Start interactive REPL mode
  -m, --model MODEL    Ollama model name
  -u, --base-url URL   Ollama server URL
  -p, --project-path PATH  Project path for context
  -h, --help           Show this help

If PROMPT is provided without --interactive, it runs one shot.
USAGE
            exit 0
            ;;
        *)
            PROMPT_INPUT="$1"
            shift
            ;;
    esac
done

if [ -n "${PROMPT_INPUT}" ] && [ "${INTERACTIVE}" = true ]; then
    echo "Error: provide either a prompt or --interactive, not both." >&2
    exit 1
fi

run_prompt() {
    local prompt="$1"
    if [ -z "${prompt}" ]; then
        return 0
    fi

    python - <<PY
import json
from integrations import create_cloudflare_agent

agent = create_cloudflare_agent(
    model="${MODEL}",
    base_url="${BASE_URL}",
    project_path="${PROJECT_PATH}",
    enable_cloudflare_mcp=False,
)

result = agent.invoke({"messages": ${prompt@Q}})
output = result.get("messages", result)
if isinstance(output, list):
    for msg in output:
        if hasattr(msg, "content"):
            print(msg.content)
        elif isinstance(msg, dict):
            print(msg.get("content", msg))
        else:
            print(msg)
else:
    print(output)
PY
}

if [ -n "${PROMPT_INPUT}" ]; then
    run_prompt "${PROMPT_INPUT}"
    exit 0
fi

if [ "${INTERACTIVE}" = false ]; then
    INTERACTIVE=true
fi

echo "DeepAgents + Ollama interactive agent"
echo "Model: ${MODEL}"
echo "Base URL: ${BASE_URL}"
echo "Project: ${PROJECT_PATH}"
echo "Type /exit or /quit to leave."
echo ""

last_prompt=""
while true; do
    if [ -n "${last_prompt}" ]; then
        echo ""
    fi

    if [ -n "${PROMPT_INPUT}" ]; then
        user_input="${PROMPT_INPUT}"
        PROMPT_INPUT=""
    else
        printf "You: "
        if [ -t 0 ]; then
            IFS= read -r user_input || user_input=""
        else
            IFS= read -r user_input || user_input=""
        fi
    fi

    case "${user_input}" in
        /exit|/quit|exit|quit)
            echo "Goodbye."
            break
            ;;
        /help|help)
            echo "Commands:"
            echo "  /exit, /quit  Exit"
            echo "  Any other text  Send prompt to Ollama agent"
            echo ""
            continue
            ;;
        "")
            if [ -z "${PROMPT_INPUT}" ]; then
                continue
            fi
            ;;
    esac

    escaped_input=$(printf "%s" "${user_input}" | sed "s/'/'\\\"'\\\"'/g")
    last_prompt="${escaped_input}"
    run_prompt "${escaped_input}"
    printf "\n"
done
