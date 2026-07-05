#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}

    if not path.exists():
        return values

    for line in path.read_text().splitlines():
        line = line.strip()

        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def read_agent_token(cloudless_dir: Path) -> str:
    env_file = cloudless_dir / ".env.local"

    if not env_file.exists():
        raise SystemExit(f"Missing {env_file}")

    for line in env_file.read_text().splitlines():
        if line.startswith("AGENT_AUTH_TOKEN="):
            token = line.split("=", 1)[1].strip()
            if token:
                return token

    raise SystemExit("Missing AGENT_AUTH_TOKEN in cloudless .env.local")


def fetch_cloudflare_result(base_url: str, token: str) -> dict:
    url = f"{base_url.rstrip('/')}/api/agents/coding-agent/default/result"

    completed = subprocess.run(
        [
            "curl",
            "-fsS",
            "-H",
            f"Authorization: Bearer {token}",
            "-H",
            "User-Agent: cloudless-local-ollama-reviewer/1.0",
            url,
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    if completed.returncode != 0:
        print(completed.stdout)
        print(completed.stderr)
        raise SystemExit("Failed to fetch Cloudflare CodingAgent result with curl.")

    return json.loads(completed.stdout)


def http_json(
    url: str,
    *,
    method: str = "POST",
    headers: dict[str, str] | None = None,
    payload: dict | None = None,
    timeout: int = 300,
) -> dict:
    body = None
    request_headers = headers or {}

    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        request_headers = {
            **request_headers,
            "Content-Type": "application/json",
        }

    request = urllib.request.Request(
        url,
        data=body,
        headers=request_headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"error": raw}
        parsed["httpStatus"] = error.code
        return parsed


def parse_structured_patch(last_response: str) -> dict:
    if not last_response.strip():
        return {}

    try:
        return json.loads(last_response)
    except json.JSONDecodeError:
        return {
            "parseError": "lastResponse is not valid JSON",
            "raw": last_response,
        }


def main() -> None:
    config = load_env_file(Path.home() / ".config" / "cloudless-coding-agent.env")

    cloudless_dir = Path(
        os.environ.get(
            "CLOUDLESS_DIR",
            config.get("CLOUDLESS_DIR", "/home/tbaltzakis/cloudless.gr"),
        )
    )

    cloudless_agent_url = os.environ.get(
        "CLOUDLESS_AGENT_URL",
        config.get(
            "CLOUDLESS_AGENT_URL",
            "https://cloudless-gr.baltzakis-themis.workers.dev",
        ),
    ).rstrip("/")

    ollama_base_url = os.environ.get(
        "OLLAMA_BASE_URL",
        config.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    ).rstrip("/")

    ollama_model = os.environ.get(
        "OLLAMA_MODEL",
        config.get("OLLAMA_MODEL", "qwen2.5-coder:latest"),
    )

    token = read_agent_token(cloudless_dir)

    cloudflare_result = fetch_cloudflare_result(cloudless_agent_url, token)

    if not cloudflare_result.get("ok"):
        print(json.dumps(cloudflare_result, indent=2))
        raise SystemExit("Cloudflare CodingAgent result was not ok.")

    last_prompt = cloudflare_result.get("lastPrompt", "")
    last_response = cloudflare_result.get("lastResponse", "")
    mode = cloudflare_result.get("mode", "")
    model = cloudflare_result.get("model", "")
    model_profile = cloudflare_result.get("modelProfile", "")
    gateway_log_id = cloudflare_result.get("gatewayLogId", "")

    structured_patch = parse_structured_patch(last_response)

    if structured_patch.get("parseError"):
        print("Verdict: NEEDS_MORE_CONTEXT")
        print()
        print("Reasoning:")
        print("- Cloudflare CodingAgent lastResponse is not valid structured patch JSON.")
        print()
        print("Safety findings:")
        print("- Do not apply anything because there is no validated structured patch object.")
        print()
        print("Suggested next commands:")
        print("- Re-run scripts/coding-agent-structured-patch.sh")
        return

    safe_to_apply = structured_patch.get("safeToApply")
    unified_diff = structured_patch.get("unifiedDiff", "")

    if safe_to_apply is not True:
        print("Verdict: DO_NOT_APPLY")
        print()
        print("Reasoning:")
        print("- Cloudflare CodingAgent set safeToApply=false.")
        print("- The patch should not be applied by policy.")
        print()
        print("Safety findings:")
        print(f"- Summary: {structured_patch.get('summary', '')}")
        print("- No local git apply should be performed.")
        print()
        print("Suggested next commands:")
        print("- No git apply command needed.")
        print("- Re-run structured patch only when you want a new proposal.")
        return

    if not isinstance(unified_diff, str) or not unified_diff.strip():
        print("Verdict: DO_NOT_APPLY")
        print()
        print("Reasoning:")
        print("- Cloudflare CodingAgent marked the patch safe, but unifiedDiff is empty.")
        print("- Empty patches should not be applied.")
        print()
        print("Safety findings:")
        print("- Missing unified diff.")
        print()
        print("Suggested next commands:")
        print("- Re-run scripts/coding-agent-structured-patch.sh with clearer patch intent.")
        return


    review_prompt = f"""
You are a local Ollama code reviewer.

You are reviewing the latest Cloudflare CodingAgent structured patch result.

Your task:
- Detect hallucinated files, imports, APIs, commands, or framework assumptions.
- Check whether the patch only changes files present in the provided repo context.
- Check whether safeToApply is reasonable.
- Check whether unifiedDiff is empty or non-empty.
- Check whether commandsToRun are correct for this repo.
- Recommend whether the human should apply the patch.

Cloudflare metadata:
- mode: {mode}
- modelProfile: {model_profile}
- model: {model}
- gatewayLogId: {gateway_log_id}

Cloudflare CodingAgent original prompt:
{last_prompt}

Cloudflare CodingAgent structured patch object:
{json.dumps(structured_patch, indent=2)}

Return exactly this structure:

Verdict: APPLY | DO_NOT_APPLY | NEEDS_MORE_CONTEXT

Reasoning:
- ...

Safety findings:
- ...

Suggested next commands:
- ...
"""

    ollama_response = http_json(
        f"{ollama_base_url}/chat/completions",
        payload={
            "model": ollama_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a careful local code-review assistant. "
                        "Do not invent files. Be conservative. "
                        "Prefer DO_NOT_APPLY when evidence is weak."
                    ),
                },
                {
                    "role": "user",
                    "content": review_prompt,
                },
            ],
            "stream": False,
        },
        timeout=300,
    )

    if "choices" not in ollama_response:
        print(json.dumps(ollama_response, indent=2))
        raise SystemExit("Ollama request failed.")

    content = ollama_response["choices"][0]["message"]["content"]
    print(content)


if __name__ == "__main__":
    main()
