"""One isolated, non-interactive Claude Code run, shared by the eval scripts.

Isolation: each run starts in a fresh empty folder, with --setting-sources project (so
the user's settings, enabled plugins and personal skills are not loaded),
--strict-mcp-config (no MCP servers) and CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
(no sync of skills uploaded to claude.ai). The only plugin a run sees is the one passed
with plugin_dir. The only tool is Skill, so a run can load a skill and nothing else.

Not isolated: the user's global CLAUDE.md, if any, is still read. It is the same in every
condition, so it shifts all conditions alike.

Author: Alex Camacho Castilho
"""
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import time

CLAUDE = shutil.which("claude") or "claude"


def long_path(path):
    """Expand Windows 8.3 short names (ALEXCA~1), which Claude Code treats as unsafe."""
    path = str(pathlib.Path(path).resolve())
    if os.name == "nt" and "~" in path:
        import ctypes
        buf = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.kernel32.GetLongPathNameW(path, buf, len(buf)):
            path = buf.value
    return path


def run_claude(prompt, model="sonnet", plugin_dir=None, system_append=None, timeout=600, retries=2):
    """Run one prompt; return result text, usage, cost, model id and skill calls."""
    cmd = [CLAUDE, "-p", prompt, "--output-format", "stream-json", "--verbose",
           "--setting-sources", "project", "--strict-mcp-config", "--tools", "Skill",
           "--model", model, "--no-session-persistence"]
    if plugin_dir:
        cmd += ["--plugin-dir", long_path(plugin_dir)]
    if system_append:
        cmd += ["--append-system-prompt", system_append]
    env = dict(os.environ, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1")
    env.pop("CLAUDECODE", None)
    last = {}
    for attempt in range(retries + 1):
        work = pathlib.Path(long_path(tempfile.mkdtemp(prefix="hb-")))
        started = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=work, env=env, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=timeout)
            last = parse_stream(proc.stdout)
            last["exit_code"] = proc.returncode
            last["stderr_tail"] = proc.stderr[-400:]
        except subprocess.TimeoutExpired:
            last = {"is_error": True, "error": "timeout"}
        finally:
            shutil.rmtree(work, ignore_errors=True)
        last["wall_seconds"] = round(time.monotonic() - started, 1)
        if not last.get("is_error") and last.get("result"):
            return last
        time.sleep(5 * (attempt + 1))
    return last


def parse_stream(stdout):
    out = {"skill_calls": [], "skills_available": [], "plugins": []}
    for line in stdout.splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") == "system" and d.get("subtype") == "init":
            out["skills_available"] = d.get("skills", [])
            out["plugins"] = [p.get("name") for p in d.get("plugins", [])]
            out["model_id"] = d.get("model")
        elif d.get("type") == "assistant":
            for c in d.get("message", {}).get("content", []):
                if c.get("type") == "tool_use" and c.get("name") == "Skill":
                    out["skill_calls"].append(c.get("input", {}).get("skill"))
        elif d.get("type") == "result":
            out["result"] = d.get("result")
            out["is_error"] = d.get("is_error", False)
            out["usage"] = d.get("usage", {})
            out["cost_usd"] = d.get("total_cost_usd")
            out["num_turns"] = d.get("num_turns")
            out["model_usage"] = d.get("modelUsage")
    return out
