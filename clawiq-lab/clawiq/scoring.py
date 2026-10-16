"""Answer parsing and traceable, versioned scoring."""
from __future__ import annotations

import json
from typing import Any
from .core import DIMENSIONS, DIMENSION_LABELS, VERSION, validate_form, fingerprint


def _equal(a: Any, b: Any) -> bool:
    """Do not allow Python's True == 1 or integer/float ambiguity."""
    if type(a) is not type(b):
        return False
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_equal(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b))
    return a == b


def parse(raw: str) -> tuple[Any, str | None]:
    if not isinstance(raw, str):
        return None, "non-string"
    try:
        # JSON.parse, not text extraction: prevents passing by echoing prompts.
        result = json.loads(raw.strip())
    except (json.JSONDecodeError, ValueError):
        return None, "invalid-json"
    if not isinstance(result, dict) or set(result) != {"answer"}:
        return None, "invalid-shape"
    return result["answer"], None


def _style(scores: dict[str, dict[str, Any]]) -> tuple[str, str]:
    pairs = [(k, v["percent"]) for k, v in scores.items() if v["count"]]
    if not pairs:
        return "待解锁", "测评完成后才能识别能力倾向"
    winner = max(pairs, key=lambda x: x[1])[0]
    return {
        "reasoning": ("规律探索虾", "目前在演绎与抽象计算任务中表现突出"),
        "instruction": ("细节执行虾", "目前在遵循多重任务约束方面表现突出"),
        "reliability": ("谨慎求证虾", "目前在识别证据不足与冲突方面表现突出"),
        "workflow": ("任务规划虾", "目前在模拟工作任务中表现突出"),
    }[winner]


def score(public: dict[str, Any], key: dict[str, Any], responses: list[dict[str, Any]], *,
          agent_label: str = "我的龙虾", mode: str = "manual", demo: bool = False) -> dict[str, Any]:
    validate_form(public, key)
    ids = [x["id"] for x in public["items"]]
    result_by_id = {}
    for row in responses:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not isinstance(row.get("raw"), str):
            raise ValueError("each response must have an id and raw text")
        ident = row["id"]
        if ident not in ids or ident in result_by_id:
            raise ValueError(f"unknown or repeated response id: {ident}")
        result_by_id[ident] = row
    if set(ids) != set(result_by_id):
        raise ValueError(f"incomplete responses: {len(result_by_id)}/{len(ids)}")
    if len(agent_label) > 80:
        raise ValueError("agent_label too long")
    question_by_id = {x["id"]: x for x in public["items"]}
    key_by_id = {x["id"]: x for x in key["answers"]}
    scores = {d: {"label": DIMENSION_LABELS[d], "correct": 0, "count": 0, "percent": 0} for d in DIMENSIONS}
    cases = []
    for ident in ids:
        row = result_by_id[ident]
        q = question_by_id[ident]
        k = key_by_id[ident]
        value, parse_error = parse(row["raw"])
        transport_error = row.get("error")
        # Distinguish invalid test run (transport/provider failure) from an
        # honest failed model answer (malformed JSON) so the score isn't inflated.
        if transport_error is not None and transport_error not in ("provider-error", "timeout", "process-error"):
            raise ValueError("unsupported transport error")
        correct = not transport_error and parse_error is None and _equal(value, k["expected"])
        dimension = q["dimension"]
        scores[dimension]["count"] += 1
        scores[dimension]["correct"] += int(correct)
        cases.append({"id": ident, "dimension": dimension, "family": q["family"],
                      "question": q["prompt"].split("\n仅输出一个严格合法的JSON对象", 1)[0],
                      "correct": bool(correct), "error": transport_error or parse_error,
                      "expected": k["expected"], "observed": (value if correct else "未通过；原始答复仅保存在本地私有文件"),
                      "reason": k["explanation"] if not correct else "答案符合客观标准"})
    for entry in scores.values():
        entry["percent"] = round(100 * entry["correct"] / entry["count"], 1)
    # A transparent weighted score, not psychometrically calibrated IQ.
    brain = round(0.45 * scores["reasoning"]["percent"] +
                  0.30 * scores["instruction"]["percent"] +
                  0.25 * scores["reliability"]["percent"], 1)
    work = scores["workflow"]["percent"]
    total = round(0.6 * brain + 0.4 * work, 1)
    invalid = any(row.get("error") is not None for row in responses)
    status = "invalid" if invalid else "complete"
    style, style_desc = _style(scores)
    ordered = sorted(scores.items(), key=lambda kv: kv[1]["percent"])
    report = {
        "schema": VERSION, "status": status, "demo": bool(demo), "mode": mode,
        "agent_label": agent_label, "suite": public["suite"], "seed": public["seed"],
        "form_commitment": public["commitment"], "sample_size": len(ids),
        "brain_score": None if invalid else brain, "task_score": None if invalid else work,
        "overall": None if invalid else total, "dimensions": scores,
        "style": {"name": style, "description": style_desc},
        "strength": DIMENSION_LABELS[ordered[-1][0]],
        "weakness": DIMENSION_LABELS[ordered[0][0]],
        "cases": cases,
        "notice": "趣味能力指数；不是人类IQ，不代表人类百分位或经心理测量校准的智商。",
        "limitations": ["题量有限；尤其 quick 只适合探索性体验，不适合严肃排名。",
                        "工作任务为模拟资料处理，不等于已经验证了真实外部工具调用。",
                        "能力画像反映该次测试表现，不表示 AI 有稳定人格或意识。"],
    }
    report["report_hash"] = fingerprint(report)
    return report


def verify_report(report: dict[str, Any], public: dict[str, Any], key: dict[str, Any],
                  responses: list[dict[str, Any]]) -> bool:
    expected = score(public, key, responses, agent_label=report["agent_label"],
                     mode=report["mode"], demo=report["demo"])
    if expected != report:
        raise ValueError("report does not agree with source answers")
    return True
