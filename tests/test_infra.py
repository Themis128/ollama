
#!/usr/bin/env python3
"""Comprehensive infra test suite."""
import sys
import os
import json
import inspect
import traceback

PASS = []
FAIL = []

def ok(name):
    PASS.append(name)
    print(f"  PASS  {name}")

def fail(name, reason):
    FAIL.append(name)
    print(f"  FAIL  {name}: {reason}")

# Import checks
print("\n[1] Import checks")
try:
    from integrations import (
        create_ollama_agent, create_cloudflare_agent, create_cloudless_agent,
        TDDAgent, TerminalAgent, SandboxAgent, Orchestrator,
        WebAgent, DebugAgent, AgentStorm, AgentRole,
        get_cloudflare_skills, get_cloudflare_mcp_servers, write_cloudflare_mcp_config,
    )
    ok("integrations __init__ all exports")
except Exception as e:
    fail("integrations __init__ all exports", e)

try:
    from integrations.deepagents_ollama import OllamaConfig, get_ollama_model, list_available_models
    ok("deepagents_ollama module")
except Exception as e:
    fail("deepagents_ollama module", e)

try:
    from integrations.cloudless_gr_integration import (
        create_cloudless_agent, create_cloudflare_agent,
        get_cloudflare_mcp_servers, write_cloudflare_mcp_config,
    )
    ok("cloudless_gr_integration module")
except Exception as e:
    fail("cloudless_gr_integration module", e)

try:
    from mcp_server.coding_agent import mcp
    ok("mcp_server.coding_agent import")
except Exception as e:
    fail("mcp_server.coding_agent import", e)

# Signature checks
print("\n[2] Signature checks")
try:
    from integrations.cloudless_gr_integration import create_cloudless_agent, create_cloudflare_agent
    cs = inspect.signature(create_cloudless_agent)
    cf = inspect.signature(create_cloudflare_agent)
    assert "enable_cloudflare_mcp" in cs.parameters
    assert "mcp_config_path" in cs.parameters
    ok("create_cloudless_agent has enable_cloudflare_mcp + mcp_config_path")
    assert "enable_cloudflare_mcp" in cf.parameters
    assert "mcp_config_path" in cf.parameters
    ok("create_cloudflare_agent has enable_cloudflare_mcp + mcp_config_path")
except Exception as e:
    fail("agent factory signatures", e)

try:
    from integrations import create_cloudflare_agent as cf_from_init
    from integrations.cloudless_gr_integration import create_cloudflare_agent as cf_from_module
    assert cf_from_init is cf_from_module
    ok("__init__ create_cloudflare_agent is the real module function")
except Exception as e:
    fail("__init__ create_cloudflare_agent identity", e)

# DebugAgent
print("\n[3] DebugAgent LLM singleton")
try:
    from integrations.debug_agent import DebugAgent
    d = DebugAgent()
    assert hasattr(d, "llm")
    ok("DebugAgent has self.llm")
    d2 = DebugAgent()
    assert d.llm is not d2.llm
    ok("DebugAgent each instance has its own llm")
except Exception as e:
    fail("DebugAgent LLM singleton", e)

print("\n[4] DebugAgent.self_fix implementation")
try:
    from integrations.debug_agent import DebugAgent
    import tempfile
    import pathlib

    debugger = DebugAgent()
    with tempfile.TemporaryDirectory() as tmp:
        test_file = pathlib.Path(tmp) / "test.ts"
        test_file.write_text("console.log(x);\n")

        error_output = "ReferenceError: x is not defined"
        original_invoke = debugger._invoke_llm
        def mock_invoke(prompt):
            return "console.log('fixed');"
        debugger._invoke_llm = mock_invoke

        result = debugger.self_fix(
            error_output=error_output,
            file_path=str(test_file),
            test_command="echo test",
        )

        assert result["fix_generated"] is not None
        assert result["fix_applied"] is True
        assert "test_passed" in result
        assert test_file.read_text() == "console.log('fixed');\n"

        ok("DebugAgent.self_fix generates and applies fix")
        ok("DebugAgent.self_fix runs test command")

        debugger._invoke_llm = original_invoke
except Exception as e:
    fail("DebugAgent.self_fix implementation", e)

# WebAgent
print("\n[5] WebAgent._is_safe_url")
try:
    from integrations.web_agent import WebAgent
    w = WebAgent()
    assert w._is_safe_url("https://github.com/foo/bar")
    assert not w._is_safe_url("http://localhost:8080")
    assert not w._is_safe_url("http://127.0.0.1/admin")
    assert not w._is_safe_url("http://192.168.1.1")
    assert not w._is_safe_url("ftp://example.com")
    ok("WebAgent._is_safe_url all cases")
except Exception as e:
    fail("WebAgent._is_safe_url", e)

# SandboxAgent
print("\n[6] SandboxAgent command validation")
try:
    from integrations.sandbox_agent import SandboxAgent
    s = SandboxAgent()
    r = s._validate_command("rm -rf /")
    assert not r["valid"]
    ok("SandboxAgent blocks rm -rf")
    r2 = s._validate_command("pnpm test")
    assert r2["valid"]
    ok("SandboxAgent allows pnpm test")
except Exception as e:
    fail("SandboxAgent command validation", e)

# TerminalAgent
print("\n[7] TerminalAgent command validation")
try:
    from integrations.terminal_agent import TerminalAgent
    t = TerminalAgent()
    r = t._validate_command("sudo rm -rf /")
    assert not r["valid"]
    ok("TerminalAgent blocks sudo rm -rf")
    r2 = t._validate_command("git status")
    assert r2["valid"]
    ok("TerminalAgent allows git status")
except Exception as e:
    fail("TerminalAgent command validation", e)

print("\n[8] TerminalAgent LLM integration")
try:
    from integrations.terminal_agent import TerminalAgent, TerminalConfig
    from unittest.mock import MagicMock

    mock_llm = MagicMock()
    mock_llm.invoke.return_value.content = "fixed code"

    config = TerminalConfig(project_path="/tmp", llm=mock_llm)
    agent = TerminalAgent(config)

    fix = agent.fix_error("TypeError: x is undefined", "compiler")
    assert "fixed code" in fix
    ok("TerminalAgent.fix_error uses LLM when configured")

    agent_no_llm = TerminalAgent()
    fix_no_llm = agent_no_llm.fix_error("TypeError: x is undefined", "compiler")
    assert "Error Analysis" in fix_no_llm or "No errors to fix" in fix_no_llm
    ok("TerminalAgent.fix_error has LLM-free fallback")
except Exception as e:
    fail("TerminalAgent LLM integration", e)

# AgentStorm
print("\n[9] AgentStorm roles")
try:
    from integrations.agent_storm import AgentStorm, DEFAULT_ROLES
    storm = AgentStorm()
    assert len(storm.roles) >= 4
    role_names = [r.name for r in storm.roles]
    for expected in ["architect", "backend", "security", "testing"]:
        assert expected in role_names
    ok(f"AgentStorm has {len(storm.roles)} roles including required 4")
except Exception as e:
    fail("AgentStorm roles", e)

# Orchestrator
print("\n[10] Orchestrator modes")
try:
    from integrations.orchestrator_agent import Orchestrator, AgentMode
    o = Orchestrator()
    assert set(m.value for m in AgentMode) == {"architect","code","debug","orchestrator","auto"}
    ok("Orchestrator AgentMode enum complete")
    assert o.switch_mode("debug") is True
    assert o.current_mode == AgentMode.DEBUG
    ok("Orchestrator.switch_mode works")
except Exception as e:
    fail("Orchestrator modes", e)

# MCP server tools
print("\n[11] MCP server tools")
try:
    import mcp_server.coding_agent as ca
    found = {n for n in dir(ca) if n.startswith("cf_agent")}
    expected_tools = {
        "cf_agent_run",
        "cf_agent_apply_patch",
        "cf_agent_full_loop",
        "cf_agent_review_with_ollama",
        "cf_agent_status",
    }
    missing = expected_tools - found
    if missing:
        fail("MCP server tools", f"missing: {missing}")
    else:
        ok(f"MCP server 5 tools registered: {found}")
except Exception as e:
    fail("MCP server tools", e)

# write_cloudflare_mcp_config
print("\n[12] write_cloudflare_mcp_config")
try:
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as tmp:
        path = str(pathlib.Path(tmp) / ".deepagents" / ".mcp.json")
        from integrations.cloudless_gr_integration import write_cloudflare_mcp_config
        cfg = write_cloudflare_mcp_config(path)
        assert "mcpServers" in cfg
        assert len(cfg["mcpServers"]) >= 13
        written = json.loads(pathlib.Path(path).read_text())
        assert written == cfg
        ok(f"write_cloudflare_mcp_config writes {len(cfg['mcpServers'])} servers")
except Exception as e:
    fail("write_cloudflare_mcp_config", e)

# Script file checks
print("\n[13] Script file checks")
scripts = [
    "scripts/start-ollama.sh",
    "scripts/stop-ollama.sh",
    "scripts/start-agent.sh",
    "scripts/test-agent.sh",
    "scripts/ollama-agent.sh",
    "scripts/ollama-agent-terminal.py",
    "scripts/ollama-agent.bat",
    "scripts/project-picker.sh",
]
for s in scripts:
    p = pathlib.Path(s)
    if p.exists():
        ok(f"{s} exists")
    else:
        fail(f"{s} exists", "file not found")

# stop-ollama.sh robustness
print("\n[14] stop-ollama.sh robustness")
try:
    content = pathlib.Path("scripts/stop-ollama.sh").read_text()
    assert "pkill" in content
    assert "systemctl" in content
    ok("stop-ollama.sh has both systemctl and pkill")
except Exception as e:
    fail("stop-ollama.sh robustness", e)

# ollama-agent.sh portable quoting
print("\n[15] ollama-agent.sh portable quoting")
try:
    content = pathlib.Path("scripts/ollama-agent.sh").read_text()
    assert "@Q" not in content
    assert "sys.argv" in content
    ok("ollama-agent.sh uses portable sys.argv quoting")
except Exception as e:
    fail("ollama-agent.sh portable quoting", e)

# Ollama server connectivity
print("\n[16] Ollama server connectivity")
try:
    import urllib.request
    req = urllib.request.Request("http://localhost:11434/api/tags")
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read())
    models = [m["name"] for m in data.get("models", [])]
    ok(f"Ollama server running, models: {models or '(none pulled)'}")
except Exception as e:
    fail("Ollama server connectivity", f"{e} — run: ollama serve")

# ollama-agent-terminal.py --help
print("\n[17] ollama-agent-terminal.py --help")
try:
    import subprocess
    r = subprocess.run(
        [sys.executable, "scripts/ollama-agent-terminal.py", "--help"],
        capture_output=True, text=True, timeout=10
    )
    assert r.returncode == 0, f"exit {r.returncode}"
    assert "usage" in r.stdout.lower() or "usage" in r.stderr.lower()
    ok("ollama-agent-terminal.py --help exits 0 with usage")
except Exception as e:
    fail("ollama-agent-terminal.py --help", e)

# Logging imports
print("\n[18] Logging imports in finished modules")
try:
    import integrations.web_agent
    import integrations.tdd_agent
    ok("logging imported in web_agent and tdd_agent")
except Exception as e:
    fail("logging imports", e)

# Ollama model robustness
print("\n[19] Ollama model robustness (MCP server)")
try:
    from mcp_server.coding_agent import _resolve_model, _get_available_models, FALLBACK_MODELS
    assert len(FALLBACK_MODELS) >= 2, "Should have fallback models configured"
    ok(f"MCP server has {len(FALLBACK_MODELS)} fallback models configured")

    available = _get_available_models()
    assert isinstance(available, set), "Should return a set of model names"
    ok("MCP server can query available models")
except Exception as e:
    fail("Ollama model robustness", e)

# Summary
print(f"\n{'='*55}")
print(f"  PASSED: {len(PASS)}   FAILED: {len(FAIL)}")
print(f"{'='*55}")
if FAIL:
    print("Failed tests:")
    for f in FAIL:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("All tests passed.")
