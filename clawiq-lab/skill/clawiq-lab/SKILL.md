---
name: clawiq-lab
description: 为自己养的 OpenClaw 智能体运行 ClawIQ 能力体检，生成可核验的趣味智力报告。用于用户明确提出测评、复测或查看报告时；不用于未经同意自动调用付费模型或改变龙虾配置。
license: MIT
metadata:
  author: ClawIQ Lab contributors
  version: "0.1.0"
---

# ClawIQ Lab — 龙虾智力研究所

## Purpose

帮助龙虾主人对自己已配置的 OpenClaw 进行一次性合成题能力测试，输出 0–100 的产品内指标、各维度优劣势和本地离线 HTML 诊断报告。

## Critical boundaries

- **你是协助操作者的测评助手，不是被测试模型的裁判。** 测评标准答案和原始结果仅供外部的 Python 评分器读取，不展示给被测龙虾。
- 用户仅要求了解功能时先说明，不要擅自开始 `run`。
- `demo` 是合成答案演示，不能声称测试了任何真实 AI。
- `run` 可能触发模型 API 扣费；仅在用户明确要求实测并同意产生调用后执行。
- 不可读取私人记忆、邮箱或工作文档；不把真实用户文件作为题目材料。不修改 OpenClaw 系统提示词、Skill、记忆或模型配置。
- **只将模拟任务视为模拟任务**，不要声称 V0.1 已验证真实工具调用或跨会话记忆。
- 不要把原始答案或私人凭证上传到 GitHub、分享到群聊或展示在公开报告中。

## Workflow

1. 在本 Skill 所属项目根目录检查 `python --version`、`python -m clawiq --help`。
2. 第一次体验使用 `python -m clawiq demo --suite quick --out ./local-demo`，并明确报告上的 DEMO 标记。
3. 需要测试真人养成龙虾且已确认调用成本时，使用 `python -m clawiq run --suite quick --out ./local-first-run --label "我的龙虾" --ack-provider-calls`。
4. 使用 `python -m clawiq verify ./local-first-run` 对表单、私有答案、原始响应与报告重新计算复核。
5. 给用户 `report.html` 和关键结论：总分、脑力/任务分、四维分、失败例子、采样限制。不能把成败归因于模型权重之外的某一配置而无证据。
6. 若用户明确要求测试已养成的真实 Gateway Agent，必须另外取得已启用工具和持久会话的知情同意，方可运行 `--backend gateway --agent-id main --ack-provider-calls --allow-existing-tools`；默认不要调用此模式。
7. 复测时换 `--seed`，把试卷、模型、运行配置、题量差异写在结论中。不同题或配置不能宣称严格可比。

## How to interpret

- **最突出**与**需关注**是相对该次四个维度的得分；小样本可能并不稳定。
- “虾格类型”是本次行为表现的趣味化归纳，不是固定人格。
- 看到 provider 失败、超时或缺题要报告无效，不允许当零分或强行补完。
- 严禁称“人类 IQ”“百分位”“全球最强”或外部权威认证。

## References

查看项目 `README.md`、`docs/METHODOLOGY.md`、`docs/SECURITY.md` 和 `docs/VALIDATION.md`。
