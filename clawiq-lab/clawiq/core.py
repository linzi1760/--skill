"""Deterministic, synthetic and objectively graded ClawIQ questions.

No existing IQ questions or benchmark test data are copied. Questions are generated
from explicit rules and answer keys kept outside the agent's question payload.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Any

VERSION = "clawiq-0.1"
DIMENSIONS = ("reasoning", "instruction", "reliability", "workflow")
SUITES = {
    "quick": {"reasoning": 4, "instruction": 3, "reliability": 3, "workflow": 2},
    "standard": {"reasoning": 12, "instruction": 10, "reliability": 10, "workflow": 8},
}
DIMENSION_LABELS = {
    "reasoning": "逻辑推理", "instruction": "理解与遵循",
    "reliability": "事实可靠性", "workflow": "模拟任务执行",
}


def fingerprint(value: Any) -> str:
    content = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _reasoning(rng: random.Random, i: int) -> tuple[str, Any, str, str]:
    if i % 2 == 0:
        m = rng.choice([17, 19, 23, 29])
        a, b, k = rng.randrange(2, m), rng.randrange(2, m), rng.randrange(2, 8)
        values = [a, b]
        for _ in range(6):
            values.append((values[-1] + 2 * values[-2] + k) % m)
        prompt = (f"给定整数序列 X0={a}, X1={b}；当 n≥2 时 Xn=(X(n-1)+2×X(n-2)+{k}) mod {m}。"
                  "请计算 X7。不要使用外部工具。")
        return prompt, values[7], "递推与模运算", "recurrence"
    a, b, c, d = (rng.randrange(3, 15) for _ in range(4))
    # Unambiguous symbolic bookkeeping in a novel story, not a recycled IQ item.
    start = a + b + c + d
    take = rng.randrange(1, min(a + b, 10))
    add = rng.randrange(2, 12)
    prompt = (f"四箱积木分别有 {a}、{b}、{c}、{d} 块。"
              f"从前两箱合计取走 {take} 块（不论分别来自哪箱），再向第四箱放入 {add} 块。"
              "现在四箱共有多少块？不要使用外部工具。")
    return prompt, start - take + add, "多条件数量推理", "quantity"


def _instruction(rng: random.Random, i: int) -> tuple[str, Any, str, str]:
    records: list[dict[str, Any]] = []
    for row in range(7):
        records.append({"id": f"P{row+1}", "price": rng.randrange(12, 40),
                        "stock": rng.randrange(0, 8), "active": rng.choice([True, True, False])})
    threshold = rng.randrange(2, 5)
    ceiling = rng.randrange(22, 38)
    selected = sorted((r for r in records if r["active"] and r["stock"] >= threshold and r["price"] <= ceiling),
                      key=lambda r: (r["price"], r["id"]))
    answer = [r["id"] for r in selected]
    prompt = ("以下商品均为模拟数据：" + json.dumps(records, ensure_ascii=False, separators=(",", ":")) +
              f"。筛选 active=true 且 stock≥{threshold} 且 price≤{ceiling} 的商品；"
              "按 price 从小到大排序，同价按 id 字母数字升序。仅返回 id 数组，没有符合条件的返回空数组。")
    return prompt, answer, "多条件筛选和排序", "filter"


def _reliability(rng: random.Random, i: int) -> tuple[str, Any, str, str]:
    owner = rng.choice(["海棠", "青松", "远山", "星河", "竹影"])
    another = rng.choice(["晓月", "白露", "春芽"])
    code = f"F-{rng.randrange(120, 980)}"
    variant = i % 3
    if variant == 0:
        records = f"文件 {code} 的负责人是{owner}，审核人是{another}。"
        key = {"status": "supported", "answer": owner}
        why = "资料直接支持负责人"
    elif variant == 1:
        records = f"文件 {code} 已创建，登记日期为2026-09-{rng.randrange(10, 29)}。未提供负责人字段。"
        key = {"status": "unknown", "answer": None}
        why = "资料缺失，不能猜测"
    else:
        records = f"记录甲：文件 {code} 的负责人是{owner}。记录乙：同一文件 {code} 的负责人是{another}。两条记录同权重，无修订信息。"
        key = {"status": "conflict", "answer": None}
        why = "资料冲突，不能任意挑选"
    prompt = ("请仅根据以下模拟资料回答，不得根据常识猜测。" + records +
              f"问题：文件 {code} 的负责人是谁？"
              '如果唯一明确则答 {"status":"supported","answer":"姓名"}；'
              '如果缺失则答 {"status":"unknown","answer":null}；'
              '如果相互冲突则答 {"status":"conflict","answer":null}。')
    return prompt, key, why, "evidence"


def _workflow(rng: random.Random, i: int) -> tuple[str, Any, str, str]:
    if i % 2 == 0:
        rows = []
        names = ["A", "B", "C", "D"]
        for j in range(8):
            rows.append({"ref": f"R{j+1}", "sku": rng.choice(names), "qty": rng.randrange(1, 11),
                         "valid": rng.choice([True, True, False])})
        chosen = rng.choice(names)
        result = sum(r["qty"] for r in rows if r["valid"] and r["sku"] == chosen)
        prompt = ("模拟文件 orders.json 内容如下：" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) +
                  f"。主人要求统计 sku={chosen} 且 valid=true 的数量合计。"
                  "请仅依据提供的文件内容计算，不要访问真实文件系统。")
        return prompt, result, "模拟数据文件处理", "virtual-data"
    durations = [rng.randrange(2, 6) for _ in range(4)]
    # A, B independent; C depends on both; D depends on B only, finish when C,D done.
    earliest = max(max(durations[0], durations[1]) + durations[2], durations[1] + durations[3])
    prompt = (f"模拟工作流：A耗时{durations[0]}小时，B耗时{durations[1]}小时；"
              f"C耗时{durations[2]}小时，必须等A和B都完成；"
              f"D耗时{durations[3]}小时，必须等B完成。"
              "任务可以并行且从0小时开始，整个项目在C和D都完成时结束。最早多少小时完成？")
    return prompt, earliest, "依赖与并行任务规划", "dependency"


GENERATOR = {"reasoning": _reasoning, "instruction": _instruction,
             "reliability": _reliability, "workflow": _workflow}


@dataclass(frozen=True)
class Form:
    public: dict[str, Any]
    key: dict[str, Any]


def generate(seed: int = 20261016, suite: str = "quick") -> Form:
    if suite not in SUITES:
        raise ValueError(f"unknown suite: {suite}")
    if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed <= 2**32 - 1:
        raise ValueError("seed must be an unsigned 32-bit integer")
    rng = random.Random(seed)
    all_items = []
    all_keys = []
    for dimension, count in SUITES[suite].items():
        for i in range(count):
            local = random.Random(rng.getrandbits(64))
            prompt, expected, why, family = GENERATOR[dimension](local, i)
            item_id = f"{dimension[:3]}-{i+1:02d}-{fingerprint([seed, suite, dimension, i, prompt])[:8]}"
            question = {"id": item_id, "dimension": dimension, "family": family,
                        "prompt": prompt + '\n仅输出一个严格合法的JSON对象，形如 {"answer":你的答案}；不要附加解释或Markdown。'}
            all_items.append(question)
            all_keys.append({"id": item_id, "dimension": dimension, "expected": expected,
                             "explanation": why})
    # Shuffle while retaining ID-key association.
    order = list(range(len(all_items)))
    rng.shuffle(order)
    items = [all_items[j] for j in order]
    keys = [all_keys[j] for j in order]
    public = {"schema": VERSION, "suite": suite, "seed": seed, "items": items,
              "notice": "Synthetic diagnostic tasks; no real files, contacts or credentials needed."}
    commitment = fingerprint(public)
    public["commitment"] = commitment
    key = {"schema": VERSION, "suite": suite, "seed": seed,
           "public_commitment": commitment, "answers": keys}
    return Form(public, key)


def validate_form(public: dict[str, Any], key: dict[str, Any]) -> None:
    if not isinstance(public, dict) or not isinstance(key, dict):
        raise ValueError("form and key must be JSON objects")
    suite = public.get("suite")
    seed = public.get("seed")
    if suite not in SUITES or not isinstance(seed, int):
        raise ValueError("invalid suite or seed")
    expected = generate(seed, suite)
    if expected.public != public or expected.key != key:
        raise ValueError("form or answer key differs from the deterministic generator")
