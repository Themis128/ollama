#!/usr/bin/env python3
"""
coding-agent MCP server
========================
Merges the 3-script Cloudflare CodingAgent + Ollama review loop into
5 MCP tools that Cline calls directly.

Tools:
  cf_agent_status          — check CF CodingAgent current state
  cf_agent_run             — send repo context + task to CF CodingAgent (review or patch)
  cf_agent_review_with_ollama — fetch CF result, review it with local Ollama, return verdict
  cf_agent_full_loop       — run + review in one call (most common)
  cf_agent_apply_patch     — apply the last structured patch to the repo

Config (env or ~/.config/cloudless-coding-agent.env):
  CLOUDLESS_DIR            — path to cloudless.gr repo (default: /home/tbaltzakis/cloudless.gr)
  CLOUDLESS_AGENT_URL      — CF Worker URL
  OLLAMA_BASE_URL          — Ollama OpenAI-compat base (default: http://localhost:11434/v1)
  OLLAMA_MODEL             — model for local review (default: qwen2.5-coder:latest)
  AGENT_AUTH_TOKEN         — read from CLOUDLESS_DIR/.env.local if not set
"""

from __future__ import annotations

import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# ── Config ─────────────────────────────────────────────────────────────────

def _load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

_cfg = _load_env_file(Path.home() / ".config" / "cloudless-coding-agent.env")

CLOUDLESS_DIR = Path(os.environ.get("CLOUDLESS_DIR", _cfg.get("CLOUDLESS_DIR", "/home/tbaltzakis/cloudless.gr")))
AGENT_URL     = os.environ.get("CLOUDLESS_AGENT_URL", _cfg.get("CLOUDLESS_AGENT_URL", "https://cloudless-gr.baltzakis-themis.workers.dev")).rstrip("/")
OLLAMA_BASE   = os.environ.get("OLLAMA_BASE_URL", _cfg.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")).rstrip("/")
OLLAMA_MODEL  = os.environ.get("OLLAMA_MODEL", _cfg.get("OLLAMA_MODEL", "qwen2.5-coder:latest"))
FALLBACK_MODELS = [
    OLLAMA_MODEL,
    "qwen2.5-coder:latest",
    "llama3.1:latest",
    "mistral:latest",
]
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))
OLLAMA_MAX_RETRIES = int(os.environ.get("OLLAMA_MAX_RETRIES", "3"))

# Validated model cache
_available_models: set[str] = set()


def _token() -> str:
    t = os.environ.get("AGENT_AUTH_TOKEN", "")
    if t:
        return t
    env_local = CLOUDLESS_DIR / ".env.local"
    if env_local.exists():
        for line in env_local.read_text().splitlines():
            if line.startswith("AGENT_AUTH_TOKEN="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError(f"AGENT_AUTH_TOKEN not found in env or {env_local}")

# ── HTTP helpers ────────────────────────────────────────────────────────────

def _http(url: str, *, method: str = "GET", headers: dict | None = None,
          payload: dict | None = None, timeout: int = 300, retries: int = OLLAMA_MAX_RETRIES) -> dict:
    body = None
    hdrs = dict(headers or {})
    if payload is not None:
        body = json.dumps(payload).encode()
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    last_exc = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            try:
                d = json.loads(raw)
            except json.JSONDecodeError:
                d = {"error": raw}
            d["httpStatus"] = e.code
            return d
        except Exception as e:
            last_exc = e
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
    return {"error": f"Request failed after {retries} retries: {last_exc}", "httpStatus": 0}

def _cf(path: str, *, method: str = "GET", payload: dict | None = None) -> dict:
    return _http(
        f"{AGENT_URL}{path}",
        method=method,
        headers={"Authorization": f"Bearer {_token()}"},
        payload=payload,
    )

# ── Repo context builder (from coding-agent-review-repo.sh) ────────────────

SOURCE_FILES = [
    "src/index.ts",
    "src/agents/coding.ts",
    "src/agents/counter.ts",
    "src/agents/echo.ts",
    "src/agents/structured-patch.ts",
    "wrangler.jsonc",
    "tsconfig.worker.json",
]

def _build_repo_context(max_chars: int = 12_000) -> str:
    sections: list[str] = []

    for rel in SOURCE_FILES:
        p = CLOUDLESS_DIR / rel
        if not p.exists():
            sections.append(f"## FILE: {rel}\nMISSING\n")
            continue
        text = p.read_text(errors="replace")
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[TRUNCATED]\n"
        sections.append(f"## FILE: {rel}\n--- BEGIN FILE ---\n{text}\n--- END FILE ---\n")

    pkg = CLOUDLESS_DIR / "package.json"
    if pkg.exists():
        p_data = json.loads(pkg.read_text())
        summary = {
            "name": p_data.get("name"),
            "version": p_data.get("version"),
            "scripts": {k: v for k, v in p_data.get("scripts", {}).items()
                        if k.startswith("cf:") or k in ("dev", "build", "typecheck", "test", "deploy")},
            "deps": {k: v for k, v in p_data.get("dependencies", {}).items()
                     if k in ("agents", "hono-agents", "openai", "@anthropic-ai/sdk")},
        }
        sections.append(f"## FILE: package.json summary\n--- BEGIN FILE ---\n{json.dumps(summary, indent=2)}\n--- END FILE ---\n")

    return "\n".join(sections)

def _build_prompt(task: str, mode: str) -> str:
    context = _build_repo_context()
    if mode == "patch":
        instructions = """
Task:
Produce a structured patch proposal.

Hard rules:
- Only propose changes to files shown above.
- If the requested capability is already implemented, set safeToApply=false.
- Never set safeToApply=true unless unifiedDiff is non-empty, minimal, and git-apply compatible.
- unifiedDiff must be a raw unified diff that can pass git apply --check.
- Do not HTML-escape characters in unifiedDiff.
- Do not invent packages, imports, files, environment variables, or framework APIs.
- commandsToRun must use existing project scripts only (pnpm, not npm).
- If unsure whether a patch applies cleanly, set safeToApply=false.
"""
    else:
        instructions = """
Task:
Review the repository context.

Review focus:
1. Worker route ordering and auth coverage
2. Agent registration and Durable Object migrations
3. Workers AI binding and AI Gateway usage
4. Production/deployment risks
5. Recommended next changes
"""
    return f"{instructions}\n\nUser task: {task}\n\nRepository context:\n\n{context}"

# ── Ollama review (from review-cloudflare-result-with-ollama.py) ────────────

def _get_available_models() -> set[str]:
    global _available_models
    if _available_models:
        return _available_models
    try:
        tags = _http(f"{OLLAMA_BASE}/api/tags", timeout=OLLAMA_TIMEOUT)
        models = {m.get("name", "") for m in tags.get("models", [])}
        _available_models = {m for m in models if m}
    except Exception:
        _available_models = set()
    return _available_models


def _resolve_model(preferred: str) -> tuple[str, str | None]:
    available = _get_available_models()
    if preferred in available:
        return preferred, None
    for fallback in FALLBACK_MODELS:
        if fallback in available:
            return fallback, f"Preferred model {preferred} not available, using {fallback}"
    return preferred, "No known models available on Ollama server"


def _ollama_review(cf_result: dict) -> str:
    last_prompt   = cf_result.get("lastPrompt", "")
    last_response = cf_result.get("lastResponse", "")
    mode          = cf_result.get("mode", "")
    model         = cf_result.get("model", "")
    gateway_log   = cf_result.get("gatewayLogId", "")

    try:
        patch = json.loads(last_response)
    except json.JSONDecodeError:
        patch = {"parseError": "lastResponse is not valid JSON", "raw": last_response}

    review_prompt = f"""
You are a local Ollama code reviewer checking a Cloudflare CodingAgent result.

Cloudflare metadata:
- mode: {mode}
- model: {model}
- gatewayLogId: {gateway_log}

Original prompt (truncated to 2000 chars):
{last_prompt[:2000]}

Cloudflare structured patch / response:
{json.dumps(patch, indent=2)[:4000]}

Your task:
- Detect hallucinated files, imports, APIs, or framework assumptions.
- Check whether the patch only touches files present in the repo context.
- Check whether safeToApply is reasonable given the unifiedDiff.
- Check whether commandsToRun are correct for this repo (pnpm, cf: scripts).
- Recommend whether the human should apply the patch.

Return exactly:

Verdict: APPLY | DO_NOT_APPLY | NEEDS_MORE_CONTEXT

Reasoning:
- ...

Safety findings:
- ...

Suggested next step:
- ...
"""

    used_model, note = _resolve_model(OLLAMA_MODEL)

    resp = _http(
        f"{OLLAMA_BASE}/chat/completions",
        method="POST",
        payload={
            "model": used_model,
            "messages": [
                {"role": "system", "content": "You are a careful local code-review assistant. Be conservative. Prefer DO_NOT_APPLY when evidence is weak."},
                {"role": "user", "content": review_prompt},
            ],
            "stream": False,
        },
        timeout=OLLAMA_TIMEOUT,
    )

    if "choices" not in resp:
        details = resp.get("error", json.dumps(resp))
        msg = "Ollama review failed (model={used_model}):\n".format(used_model=used_model)
        msg += "{details}\n\n".format(details=details)
        msg += "Recommended action:\n"
        msg += "- Confirm Ollama is running: ollama list\n"
        msg += "- Verify model availability: ollama pull {model}\n".format(model=used_model)
        msg += "- Check OLLAMA_BASE_URL={base}\n".format(base=OLLAMA_BASE)
        msg += "- Check OLLAMA_MODEL={model}".format(model=used_model)
        return msg
    content = resp["choices"][0]["message"]["content"]
    if note:
        content = "[model-note] {note}\n\n".format(note=note) + content

    return content

# ── MCP server ──────────────────────────────────────────────────────────────

mcp = FastMCP("coding-agent")

@mcp.tool()
def cf_agent_status() -> str:
    """Check the current state of the Cloudflare CodingAgent (status, last mode, model, error)."""
    result = _cf("/api/agents/coding-agent/default/status")
    return json.dumps(result, indent=2)


@mcp.tool()
def cf_agent_run(task: str, mode: str = "review", model_profile: str = "review") -> str:
    """
    Send a task to the Cloudflare CodingAgent with full repo context.

    Args:
        task: What you want the agent to do (e.g. 'review auth coverage' or 'propose patch to add X').
        mode: 'review' (default) or 'patch'.
        model_profile: 'fast' | 'review' | 'deep' (default: review; use deep for patch).
    """
    prompt = _build_prompt(task, mode)
    payload = {"prompt": prompt, "mode": mode, "modelProfile": model_profile}

    if mode == "patch":
        result = _cf("/api/agents/coding-agent/default/structured-patch", method="POST", payload=payload)
    else:
        result = _cf("/api/agents/coding-agent/default/task", method="POST", payload=payload)

    return json.dumps(result, indent=2)


@mcp.tool()
def cf_agent_review_with_ollama() -> str:
    """
    Fetch the latest Cloudflare CodingAgent result and review it with local qwen2.5-coder.
    Returns a verdict: APPLY | DO_NOT_APPLY | NEEDS_MORE_CONTEXT plus reasoning.
    """
    cf_result = _cf("/api/agents/coding-agent/default/result")
    if not cf_result.get("ok"):
        return f"CF agent returned error:\n{json.dumps(cf_result, indent=2)}"

    verdict = _ollama_review(cf_result)

    # Save patch if safeToApply
    try:
        patch_obj = json.loads(cf_result.get("lastResponse", ""))
        if patch_obj.get("safeToApply") and patch_obj.get("unifiedDiff", "").strip():
            patches_dir = CLOUDLESS_DIR / "patches" / "coding-agent"
            patches_dir.mkdir(parents=True, exist_ok=True)
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            patch_file = patches_dir / f"patch-{ts}.patch"
            patch_file.write_text(patch_obj["unifiedDiff"])
            verdict += f"\n\n✅ Patch saved to: {patch_file}"
    except (json.JSONDecodeError, KeyError):
        pass

    return verdict


@mcp.tool()
def cf_agent_full_loop(task: str, mode: str = "patch", model_profile: str = "deep") -> str:
    """
    Run the full loop in one call: send task to CF CodingAgent → fetch result → review with Ollama.
    Returns the Ollama verdict with reasoning.

    Args:
        task: What you want done (e.g. 'add rate limiting to /api/agents routes').
        mode: 'review' or 'patch' (default: patch).
        model_profile: 'fast' | 'review' | 'deep' (default: deep for patch quality).
    """
    # Step 1: send to CF
    prompt = _build_prompt(task, mode)
    payload = {"prompt": prompt, "mode": mode, "modelProfile": model_profile}

    if mode == "patch":
        _cf("/api/agents/coding-agent/default/structured-patch", method="POST", payload=payload)
    else:
        _cf("/api/agents/coding-agent/default/task", method="POST", payload=payload)

    # Step 2: fetch result
    cf_result = _cf("/api/agents/coding-agent/default/result")
    if not cf_result.get("ok"):
        return f"CF agent error:\n{json.dumps(cf_result, indent=2)}"

    # Step 3: Ollama review
    verdict = _ollama_review(cf_result)

    # Save patch if safe
    try:
        patch_obj = json.loads(cf_result.get("lastResponse", ""))
        if patch_obj.get("safeToApply") and patch_obj.get("unifiedDiff", "").strip():
            patches_dir = CLOUDLESS_DIR / "patches" / "coding-agent"
            patches_dir.mkdir(parents=True, exist_ok=True)
            from datetime import datetime, timezone
            ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
            patch_file = patches_dir / f"patch-{ts}.patch"
            patch_file.write_text(patch_obj["unifiedDiff"])
            verdict += f"\n\n✅ Patch saved to: {patch_file}"
    except (json.JSONDecodeError, KeyError):
        pass

    return verdict


@mcp.tool()
def cf_agent_apply_patch(patch_file: str = "", run_typecheck: bool = True) -> str:
    """
    Apply a saved patch to the cloudless.gr repo on a new branch.
    Runs cf:typecheck after applying. Rolls back on failure.

    Args:
        patch_file: Absolute path to .patch file. Omit to use the latest in patches/coding-agent/.
        run_typecheck: Run pnpm cf:typecheck after apply (default: True).
    """
    repo = CLOUDLESS_DIR

    # Resolve patch file
    if not patch_file:
        patches_dir = repo / "patches" / "coding-agent"
        candidates = sorted(patches_dir.glob("*.patch"), reverse=True)
        if not candidates:
            return "No patch files found in patches/coding-agent/"
        patch_path = candidates[0]
    else:
        patch_path = Path(patch_file)

    if not patch_path.exists():
        return f"Patch file not found: {patch_path}"

    def run(cmd: list[str], **kw: Any) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, cwd=repo, capture_output=True, text=True, **kw)

    # Check working tree is clean
    dirty = run(["git", "diff", "--quiet"])
    dirty_cached = run(["git", "diff", "--cached", "--quiet"])
    if dirty.returncode != 0 or dirty_cached.returncode != 0:
        return "Refusing to apply: working tree is not clean. Commit or stash changes first."

    # Dry-run check
    check = run(["git", "apply", "--check", str(patch_path)])
    if check.returncode != 0:
        return f"Patch does not apply cleanly:\n{check.stderr}"

    # Create branch
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    branch = f"agentic/apply-{ts}"
    run(["git", "checkout", "-b", branch])

    # Apply
    apply = run(["git", "apply", str(patch_path)])
    if apply.returncode != 0:
        run(["git", "reset", "--hard", "HEAD"])
        run(["git", "checkout", "-"])
        return f"git apply failed:\n{apply.stderr}"

    # Typecheck
    if run_typecheck:
        tc = run(["pnpm", "run", "cf:typecheck"])
        if tc.returncode != 0:
            run(["git", "reset", "--hard", "HEAD"])
            return f"Typecheck failed — patch reverted:\n{tc.stdout}\n{tc.stderr}"

    diff = run(["git", "diff", "--stat", "HEAD"])
    return (
        f"✅ Patch applied on branch: {branch}\n"
        f"Patch file: {patch_path}\n\n"
        f"Diff stat:\n{diff.stdout}\n\n"
        f"Next steps:\n"
        f"  git diff                          # review changes\n"
        f"  git add -A && git commit -m '...' # commit\n"
        f"  pnpm run cf:deploy                # deploy to Cloudflare\n"
        f"  git push -u origin {branch}       # push branch"
    )


if __name__ == "__main__":
    mcp.run()
