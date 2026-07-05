#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="${CONFIG_FILE:-$HOME/.config/cloudless-coding-agent.env}"

if [ -f "$CONFIG_FILE" ]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

CLOUDLESS_DIR="${CLOUDLESS_DIR:-/home/tbaltzakis/cloudless.gr}"
CLOUDLESS_AGENT_URL="${CLOUDLESS_AGENT_URL:-https://cloudless-gr.baltzakis-themis.workers.dev}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen2.5-coder:latest}"

echo "==> Cloudless dir: $CLOUDLESS_DIR"
echo "==> Cloudflare CodingAgent: $CLOUDLESS_AGENT_URL"
echo "==> Ollama model: $OLLAMA_MODEL"
echo

cd "$CLOUDLESS_DIR"

echo "==> Step 1: Requesting structured patch from Cloudflare CodingAgent..."
scripts/coding-agent-structured-patch.sh "$CLOUDLESS_AGENT_URL"

echo
echo "==> Step 2: Trying to save patch locally with safety gates..."
set +e
SAVE_OUTPUT="$(scripts/coding-agent-save-structured-patch.sh "$CLOUDLESS_AGENT_URL" 2>&1)"
SAVE_EXIT=$?
set -e

echo "$SAVE_OUTPUT"

PATCH_FILE=""

if [ "$SAVE_EXIT" -eq 0 ]; then
  PATCH_FILE="$(echo "$SAVE_OUTPUT" | awk '/Saved patch:/ {print $3}' | tail -n1)"
fi

echo
echo "==> Step 3: Running local Ollama second reviewer..."
cd /home/tbaltzakis/ollama

OLLAMA_MODEL="$OLLAMA_MODEL" scripts/cloudless-review-last.sh

echo
echo "==> Step 4: Decision helper"

if [ "$SAVE_EXIT" -ne 0 ]; then
  echo "No patch was saved. Do NOT apply anything."
  echo "Reason: save script refused the patch or no safe patch exists."
  exit 0
fi

if [ -z "$PATCH_FILE" ]; then
  echo "Save script succeeded but no patch path was detected. Do NOT apply automatically."
  exit 1
fi

echo "A patch was saved:"
echo "  $PATCH_FILE"
echo
echo "Manual apply flow:"
echo "  cd $CLOUDLESS_DIR"
echo "  git apply --check $PATCH_FILE"
echo "  git apply $PATCH_FILE"
echo "  pnpm run cf:typecheck"
echo
echo "Apply only if YOU agree with the Cloudflare result and Ollama review."
