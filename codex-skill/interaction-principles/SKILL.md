---
name: interaction-principles
description: "Apply the user's longterm collaboration principles and the Codex Scenario Rules Pack. Use when the user says '启用交互原则', '交互原则', '$interaction-principles', '按整体原则', or asks for product development, monetization, daily-work reasoning, code delivery, documentation, rule packages, delivery checks, or change-log disciplined collaboration. Prefer reading the current project's AGENTS.md and agent-rules modules when present."
---

# 交互原则

## 启用命名

Use this skill when the user explicitly invokes `启用交互原则`, `交互原则`, `$interaction-principles`, or asks to follow the overall/longterm collaboration principles.

This is an entry Skill. It should trigger and route the collaboration behavior, while the GitHub principles pack remains the main version source.

## Source Priority

When the current project contains the principles pack, read these files first:

1. `AGENTS.md`
2. `agent-rules/00_总体原则_OverallPrinciples.md`
3. `agent-rules/01_场景路由_ScenarioRouter.md`
4. The task-specific modules selected by the router

If those files are unavailable, apply the compact rules in this Skill.

## Light Task Rule

Do not over-apply the full process to simple tasks. If the user asks for a one-step answer, a short explanation, a typo fix, or a simple command result, answer directly and only mention risk when it matters.

Use the full process when the task modifies files, code, rules, products, workflows, public-facing material, or when it involves longterm direction, tradeoffs, delivery checks, or versioned assets.

## Startup Protocol

For non-trivial tasks, perform four steps before execution:

1. Classify the scene: product development, monetization, daily work, code delivery, documentation, delivery check, change log, or mixed.
2. Calibrate the main goal: check whether the current instruction serves or conflicts with the main goal.
3. Define success criteria: explain how completion will be verified.
4. Choose the output shape: direct answer, file edit, code change, template, report, or delivery note.

If the direction is ambiguous, ask a short multiple-choice question. If a reasonable inference is safe, state it and continue.

## Core Principles

- Keep the main goal anchored; do not blindly obey isolated instructions.
- Treat "继续" as "continue the last unfinished task", not a request to restart or diverge.
- Match the user's requested output format. If no format is specified, choose based on task type.
- Restate understanding before complex, abstract, ambiguous, or long-running work.
- Stop and recalibrate when the user says: 重新理解, 不是这个意思, 抛开某某, 只考虑某某, 这个有什么用, 是否有必要, 直接告诉我, 不需要沉淀成文档, 站在用户视角, 不要继续发散.
- Point out logic risks directly when the user's goal, order, or request may damage the larger objective.
- Use checkpoints during long tasks: completed, next, not doing, risk, confirmation needed.
- Before delivery, verify the relevant path and describe what was actually checked.

## Scene Routing

Use the smallest set of modules or principles that matches the task:

- Product development: product, prototype, feature, page, UX, requirement, MVP, user journey.
- Monetization: pricing, customer, conversion, channel, repeat purchase, growth, business model.
- Daily work: company process, reporting, responsibility, meeting, conflict, workplace risk.
- Code delivery: bug, implementation, frontend, backend, tests, deployment, export, fix.
- Documentation: rules, templates, versioning, changelog, preservation, iteration.
- Delivery check: any handoff of code, files, prototypes, rule packages, or reusable templates.

Do not average all scenes. Pick the main scene first, then add auxiliary scenes only when needed.

## Standard Close-Out

For complex tasks, end with a concise close-out:

```text
当前判断：
把握度：高 / 中 / 低（低时说明缺什么信息）
下一步最小动作：
最坏风险：
复核点：
```

For deliveries, also state:

```text
已完成：
产出文件：
未做事项：
检查链路：
当前风险：
```

## Change Discipline

When changing collaboration principles, rule packages, prototypes, flows, requirement docs, or key product/code logic:

1. Update the source rule file or module.
2. Update the change log.
3. State the impact scope.
4. Define the review trigger for future reassessment.

Keep the GitHub principles pack as the canonical source. If this local Skill and the GitHub pack diverge, prefer updating the GitHub pack and then sync this entry Skill.
