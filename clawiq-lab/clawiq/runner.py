"""Optional OpenClaw adapter. No paid calls or external tools in offline/demo mode."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class RunnerUnavailable(RuntimeError):
    pass


def check_openclaw_cli(*, backend: str = "isolated") -> None:
    """Check the installed CLI interface without any provider/model requests."""
    if backend not in ("isolated", "gateway"):
        raise ValueError("unsupported OpenClaw backend")
    if shutil.which("openclaw") is None:
        raise RunnerUnavailable("OpenClaw CLI is not installed in PATH")
    cmd = ["openclaw", "agent", "exec", "--help"] if backend == "isolated" else ["openclaw", "agent", "--help"]
    required = (("--message-file", "--cwd", "--json", "--code-mode", "--config-override", "--timeout")
                if backend == "isolated" else
                ("--message-file", "--agent", "--session-id", "--json", "--timeout"))
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunnerUnavailable("OpenClaw CLI preflight failed") from exc
    if proc.returncode:
        raise RunnerUnavailable("OpenClaw CLI help returned an error")
    missing = [flag for flag in required if flag not in proc.stdout + "\n" + proc.stderr]
    if missing:
        raise RunnerUnavailable("Unsupported OpenClaw CLI: missing " + ", ".join(missing))


def extract_openclaw_text(text: str) -> str:
    """Stable `openclaw agent exec --json` envelope since 2026.

    Never pretend text is a passing response when the agent failed.
    """
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RunnerUnavailable("OpenClaw did not return JSON") from exc
    if not isinstance(result, dict) or result.get("ok") is not True or result.get("status") != "ok":
        raise RunnerUnavailable("OpenClaw reported an unsuccessful run")
    tool_summary = result.get("toolSummary")
    if isinstance(tool_summary, dict) and "calls" in tool_summary:
        calls = tool_summary["calls"]
        if type(calls) is not int or calls != 0:
            raise RunnerUnavailable("Tool activity detected during a no-tools cognitive test")
    answer = result.get("final")
    if not isinstance(answer, str) or not answer.strip():
        raise RunnerUnavailable("OpenClaw returned no final text")
    return answer


def invoke_openclaw(prompt: str, *, timeout: int = 120) -> dict[str, Any]:
    if shutil.which("openclaw") is None:
        raise RunnerUnavailable("OpenClaw CLI is not installed in PATH")
    with tempfile.TemporaryDirectory(prefix="clawiq-eval-") as tmp:
        root = Path(tmp)
        prompt_path = root / "question.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        # Isolated per question: fresh one-shot agent state and workspace.
        # Explicit tool denial is stronger than the minimal profile alone.
        # This is NOT an operating-system/container sandbox.
        override = {"tools": {"profile": "minimal", "deny": ["*"]},
                    "agents": {"defaults": {"contextInjection": "never"}}}
        args = ["openclaw", "agent", "exec", "--message-file", str(prompt_path),
                "--cwd", str(root), "--json", "--timeout", str(timeout),
                "--code-mode", "direct",
                "--config-override", json.dumps(override, separators=(",", ":"))]
        try:
            completed = subprocess.run(args, cwd=root, capture_output=True, text=True,
                                       timeout=timeout + 30, check=False)
        except subprocess.TimeoutExpired as exc:
            raise RunnerUnavailable("OpenClaw attempt timed out") from exc
        if completed.returncode != 0:
            raise RunnerUnavailable(f"OpenClaw exited with code {completed.returncode}")
        raw = extract_openclaw_text(completed.stdout)
        try:
            meta = json.loads(completed.stdout)
        except json.JSONDecodeError:
            meta = {}
        return {"raw": raw, "usage": meta.get("usage") if isinstance(meta.get("usage"), dict) else None,
                "cost_usd": meta.get("costUsd") if isinstance(meta.get("costUsd"), (int, float)) else None}


def invoke_gateway_agent(prompt: str, *, agent_id: str = "main", timeout: int = 120) -> dict[str, Any]:
    """Opt-in: test the *existing* configured OpenClaw agent.

    This reuses an active Gateway and its installed tools/skills. It does NOT
    sandbox user tools; only use after explicit owner approval. No --deliver.
    """
    import uuid
    if shutil.which("openclaw") is None:
        raise RunnerUnavailable("OpenClaw CLI is not installed in PATH")
    if not agent_id or len(agent_id) > 64 or not all(c.isalnum() or c in "-_" for c in agent_id):
        raise ValueError("agent_id must consist of ASCII letters, digits, hyphen or underscore")
    with tempfile.TemporaryDirectory(prefix="clawiq-gateway-question-") as tmp:
        prompt_path = Path(tmp) / "question.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        args = ["openclaw", "agent", "--agent", agent_id,
                "--session-id", str(uuid.uuid4()),
                "--message-file", str(prompt_path), "--json", "--timeout", str(timeout)]
        try:
            completed = subprocess.run(args, capture_output=True, text=True, timeout=timeout+30, check=False)
        except subprocess.TimeoutExpired as exc:
            raise RunnerUnavailable("Gateway attempt timed out or may still be running") from exc
        if completed.returncode != 0:
            raise RunnerUnavailable(f"Gateway exited with code {completed.returncode}; inspect Gateway state before retry")
        try:
            data = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise RunnerUnavailable("Gateway returned non-JSON data") from exc
        if not isinstance(data, dict) or data.get("ok") is False or data.get("status") in ("error", "timeout", "in_flight"):
            raise RunnerUnavailable("Gateway reported failure or ambiguous status")
        payload = data.get("result") if isinstance(data.get("result"), dict) else data
        replies = payload.get("payloads") if isinstance(payload.get("payloads"), list) else []
        messages = [x["text"] for x in replies if isinstance(x, dict) and isinstance(x.get("text"), str)]
        if not messages:
            raise RunnerUnavailable("Gateway did not provide a valid reply payload")
        return {"raw": messages[-1], "usage": None, "cost_usd": None}
