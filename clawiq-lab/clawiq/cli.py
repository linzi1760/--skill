"""Command line workflow: generate / run / score / verify / render / demo."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from .core import SUITES, generate, validate_form
from .reporting import render_html
from .runner import invoke_openclaw, invoke_gateway_agent, check_openclaw_cli, RunnerUnavailable
from .scoring import score, verify_report


def save(path: Path, value: Any, *, private: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(str(path), flags, 0o600 if private else 0o644)
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write("\n")


def read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _init_form(out: Path, suite: str, seed: int) -> tuple[dict, dict]:
    out.mkdir(parents=True, exist_ok=False)
    form = generate(seed, suite)
    save(out / "form.public.json", form.public)
    save(out / "answer-key.private.json", form.key, private=True)
    return form.public, form.key


def _finish(out: Path, public: dict, key: dict, responses: list[dict], *,
            mode: str, label: str, demo: bool) -> dict:
    result = score(public, key, responses, mode=mode, agent_label=label, demo=demo)
    save(out / "responses.private.json", responses, private=True)
    save(out / "report.json", result)
    (out / "report.html").write_text(render_html(result), encoding="utf-8")
    return result


def command_demo(args: argparse.Namespace) -> int:
    out = Path(args.out)
    public, key = _init_form(out, args.suite, args.seed)
    rows = []
    for i, answer in enumerate(key["answers"]):
        expected = answer["expected"]
        # These are generated examples, never actual OpenClaw answers.
        if i in {2, 6, 9}:
            value = {"answer": "example-wrong-answer"}
        else:
            value = {"answer": expected}
        rows.append({"id": answer["id"], "raw": json.dumps(value, ensure_ascii=False)})
    result = _finish(out, public, key, rows, mode="synthetic", label="演示龙虾 · 非真实测试", demo=True)
    print(f"DEMO ONLY (synthetic answers): {out / 'report.html'} | score={result['overall']}")
    return 0


def command_generate(args: argparse.Namespace) -> int:
    public, _ = _init_form(Path(args.out), args.suite, args.seed)
    print(f"Generated {len(public['items'])} synthetic questions; answer key is private: {args.out}")
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    check_openclaw_cli(backend=args.backend)
    print(f"READY: {args.backend} CLI flags verified; no model calls made")
    return 0


def command_run(args: argparse.Namespace) -> int:
    if not args.ack_provider_calls:
        raise ValueError("Live tests may consume API tokens. Pass --ack-provider-calls to opt in.")
    if args.backend == "gateway" and not args.allow_existing_tools:
        raise ValueError("Gateway mode uses your real agent and installed tools. Pass --allow-existing-tools to opt in explicitly.")
    if not 10 <= args.timeout <= 1800:
        raise ValueError("--timeout must be between 10 and 1800 seconds")
    check_openclaw_cli(backend=args.backend)
    out = Path(args.out)
    public, key = _init_form(out, args.suite, args.seed)
    rows: list[dict[str, Any]] = []
    for i, item in enumerate(public["items"], 1):
        try:
            if args.backend == "gateway":
                attempt = invoke_gateway_agent(item["prompt"], agent_id=args.agent_id, timeout=args.timeout)
            else:
                attempt = invoke_openclaw(item["prompt"], timeout=args.timeout)
            row = {"id": item["id"], "raw": attempt["raw"]}
        except RunnerUnavailable as exc:
            # No raw traceback, config, stderr, keys, or private workspace data.
            row = {"id": item["id"], "raw": "", "error": "process-error"}
            print(f"Test {i}: provider failure ({exc}). Marking entire run invalid.", file=sys.stderr)
        rows.append(row)
        print(f"[{i}/{len(public['items'])}] {item['dimension']} recorded")
        # Private checkpoint survives provider failures and interrupts.
        checkpoint = out / "responses.checkpoint.private.json"
        checkpoint.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        try:
            checkpoint.chmod(0o600)
        except OSError:
            pass
        if row.get("error"):
            print("Stopped after first provider failure; no valid score will be published.", file=sys.stderr)
            break
    if len(rows) != len(public["items"]):
        print(f"Incomplete live run: {len(rows)}/{len(public['items'])}; retained private checkpoint.", file=sys.stderr)
        return 2
    result = _finish(out, public, key, rows, mode=("openclaw-gateway" if args.backend == "gateway" else "openclaw-exec"), label=args.label, demo=False)
    (out / "responses.checkpoint.private.json").unlink(missing_ok=True)
    if result["status"] != "complete":
        print("Invalid run due to provider failure.", file=sys.stderr)
        return 2
    print(f"REPORT: {out / 'report.html'} | score={result['overall']}")
    return 0


def command_score(args: argparse.Namespace) -> int:
    out = Path(args.form_dir)
    public = read(out / "form.public.json")
    key = read(out / "answer-key.private.json")
    responses = read(Path(args.responses))
    if not isinstance(responses, list):
        raise ValueError("responses JSON must contain a list of {id,raw}")
    # Preserve the original response location; write score artifacts to new dir.
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=False)
    save(dest / "form.public.json", public)
    save(dest / "answer-key.private.json", key, private=True)
    result = _finish(dest, public, key, responses, mode="manual-import", label=args.label, demo=False)
    print(f"Scored as {result['status']}: {dest / 'report.html'}")
    return 0 if result["status"] == "complete" else 2


def command_verify(args: argparse.Namespace) -> int:
    out = Path(args.directory)
    public, key, responses, report = (read(out / name) for name in (
        "form.public.json", "answer-key.private.json", "responses.private.json", "report.json"))
    validate_form(public, key)
    verify_report(report, public, key, responses)
    print(f"VERIFIED: {out} | sample={report['sample_size']} | {report['status']}")
    return 0


def command_render(args: argparse.Namespace) -> int:
    result = read(Path(args.report))
    target = Path(args.out)
    if target.exists():
        raise FileExistsError(f"refusing to overwrite {target}")
    target.write_text(render_html(result), encoding="utf-8")
    print(f"REPORT HTML: {target}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="clawiq", description="ClawIQ Lab - test your OpenClaw 🦞")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("demo", "generate", "run"):
        cmd = commands.add_parser(name)
        cmd.add_argument("--suite", choices=list(SUITES), default="quick")
        cmd.add_argument("--seed", type=int, default=20261016)
        cmd.add_argument("--out", required=True, help="new output folder (must not exist)")
    commands.choices["run"].add_argument("--label", default="我的龙虾")
    commands.choices["run"].add_argument("--backend", choices=["isolated", "gateway"], default="isolated")
    commands.choices["run"].add_argument("--agent-id", default="main", help="only for gateway backend")
    commands.choices["run"].add_argument("--allow-existing-tools", action="store_true", help="ack real Gateway agent context, tools and persistent session effects")
    commands.choices["run"].add_argument("--timeout", type=int, default=120, help="seconds per question")
    commands.choices["run"].add_argument("--ack-provider-calls", action="store_true")
    doctor = commands.add_parser("doctor", help="read-only CLI preflight; no model calls")
    doctor.add_argument("--backend", choices=["isolated", "gateway"], default="isolated")
    imp = commands.add_parser("score", help="score external/manual response JSON list")
    imp.add_argument("--form-dir", required=True)
    imp.add_argument("--responses", required=True)
    imp.add_argument("--out", required=True)
    imp.add_argument("--label", default="我的龙虾")
    verify = commands.add_parser("verify")
    verify.add_argument("directory")
    render = commands.add_parser("render")
    render.add_argument("--report", required=True)
    render.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    funcs = {"demo": command_demo, "generate": command_generate, "run": command_run,
             "doctor": command_doctor, "score": command_score,
             "verify": command_verify, "render": command_render}
    try:
        return funcs[args.command](args)
    except (ValueError, FileNotFoundError, FileExistsError, PermissionError, RunnerUnavailable) as exc:
        print(f"ClawIQ error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
