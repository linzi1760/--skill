"""Optional OpenClaw adapter. No paid calls or external tools in offline/demo mode."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


class RunnerUnavailable(RuntimeError):
    pass


def check_openclaw_cli(*, backend: str = "isolated", model: str | None = None) -> str:
    """Check the installed CLI interface without any provider/model requests."""
    if backend not in ("isolated", "gateway"):
        raise ValueError("unsupported OpenClaw backend")
    if shutil.which("openclaw") is None:
        raise RunnerUnavailable("OpenClaw CLI is not installed in PATH")
    cmd = ["openclaw", "agent", "exec", "--help"] if backend == "isolated" else ["openclaw", "agent", "--help"]
    required = (("--message-file", "--cwd", "--json", "--code-mode", "--timeout")
                if backend == "isolated" else
                ("--message-file", "--agent", "--session-id", "--json", "--timeout"))
    try:
        if model is not None:
            with tempfile.TemporaryDirectory(prefix="clawiq-preflight-") as tmp:
                env = {"PATH": os.environ.get("PATH", ""), "HOME": tmp, "USERPROFILE": tmp,
                       "XDG_CONFIG_HOME": tmp, "OPENCLAW_STATE_DIR": str(Path(tmp) / "state"),
                       "OPENCLAW_CONFIG_PATH": str(Path(tmp) / "absent.json"),
                       "OPENCLAW_CONFIG_READONLY": "1"}
                if "SYSTEMROOT" in os.environ:
                    env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
                proc = subprocess.run(cmd, env=env, cwd=tmp, capture_output=True, text=True, timeout=15, check=False)
        else:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunnerUnavailable("OpenClaw CLI preflight failed") from exc
    if proc.returncode:
        raise RunnerUnavailable("OpenClaw CLI help returned an error")
    help_text = proc.stdout + "\n" + proc.stderr
    missing = [flag for flag in required if flag not in help_text]
    if missing:
        raise RunnerUnavailable("Unsupported OpenClaw CLI: missing " + ", ".join(missing))
    if backend == "gateway":
        return "gateway"
    if model is None and "--config-override" in help_text:
        return "override"
    if "--config <" in help_text and "--model" in help_text:
        if not model:
            raise RunnerUnavailable("This CLI requires an explicit --model provider/model for a credential-isolated config; optionally select --provider-env NAME. No ambient config will be imported.")
        validate_model_options(model, [])
        return "config"
    raise RunnerUnavailable("Unsupported OpenClaw CLI: safe configuration interface is unavailable")


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
    if not isinstance(tool_summary, dict) or type(tool_summary.get("calls")) is not int:
        raise RunnerUnavailable("No-tools execution evidence missing or invalid")
    if tool_summary["calls"] != 0:
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



PROVIDER_ENV_NAMES = frozenset({"OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"})


def validate_model_options(model: str | None, provider_env: list[str]) -> None:
    if model is not None and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*/[A-Za-z0-9][A-Za-z0-9_./:-]{0,180}", model):
        raise ValueError("--model must be an explicit provider/model identifier")
    if provider_env and not model:
        raise ValueError("--provider-env requires --model")
    if any(name not in PROVIDER_ENV_NAMES for name in provider_env):
        raise ValueError("Unsupported --provider-env name; allowed: " + ", ".join(sorted(PROVIDER_ENV_NAMES)))


def minimal_config() -> dict[str, Any]:
    return {"tools": {"profile": "minimal", "deny": ["*"]},
            "agents": {"defaults": {"contextInjection": "never", "skipBootstrap": True}},
            "plugins": {"enabled": False}, "env": {"shellEnv": {"enabled": False}}}


def invoke_configured_openclaw(prompt: str, *, model: str, provider_env: list[str],
                              timeout: int = 120) -> dict[str, Any]:
    """Explicit minimal configuration; never read or copy operator config/stores.

    Provider env names must be selected by the operator. Values stay in the
    child environment, never in config, command arguments, reports or logs.
    This restricts discovery; it is not an OS/network sandbox.
    """
    validate_model_options(model, provider_env)
    executable = shutil.which("openclaw")
    if executable is None:
        raise RunnerUnavailable("OpenClaw CLI is not installed in PATH")
    with tempfile.TemporaryDirectory(prefix="clawiq-config-eval-") as tmp:
        root = Path(tmp)
        config = root / "openclaw.json"
        with config.open("x", encoding="utf-8") as file:
            os.chmod(config, 0o600)
            json.dump(minimal_config(), file)
        prompt_path = root / "question.md"
        prompt_path.write_text(prompt, encoding="utf-8")
        env = {"PATH": os.environ.get("PATH", ""), "HOME": tmp, "USERPROFILE": tmp,
               "XDG_CONFIG_HOME": tmp, "OPENCLAW_STATE_DIR": str(root / "state"),
               "OPENCLAW_CONFIG_PATH": str(config), "OPENCLAW_CONFIG_READONLY": "1"}
        if "SYSTEMROOT" in os.environ:
            env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
        for name in provider_env:
            if not os.environ.get(name):
                raise RunnerUnavailable("Selected provider environment variable is missing: " + name)
            env[name] = os.environ[name]
        args = [executable, "agent", "exec", "--message-file", str(prompt_path),
                "--cwd", tmp, "--config", str(config), "--model", model,
                "--code-mode", "direct", "--json", "--timeout", str(timeout)]
        try:
            completed = subprocess.run(args, cwd=tmp, env=env, capture_output=True,
                                       text=True, timeout=timeout + 30, check=False)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RunnerUnavailable("Explicit-config OpenClaw process failed or timed out") from exc
        if completed.returncode != 0:
            raise RunnerUnavailable(f"OpenClaw exited with code {completed.returncode}")
        raw = extract_openclaw_text(completed.stdout)
        meta = json.loads(completed.stdout)
        summary = meta.get("toolSummary")
        if not isinstance(summary, dict) or type(summary.get("calls")) is not int or summary["calls"] != 0:
            raise RunnerUnavailable("No-tools execution evidence missing or invalid")
        return {"raw": raw, "usage": meta.get("usage"), "cost_usd": meta.get("costUsd")}
