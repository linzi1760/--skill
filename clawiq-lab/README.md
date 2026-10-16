# 🦞 ClawIQ Lab · 龙虾智力评测

**测测你养的龙虾有多聪明，看清它的强项与短板。**

ClawIQ Lab 是面向个人 AI 智能体的开源能力测评工具。通过动态题目、独立评分和趣味报告，帮助你**认识自己的龙虾，而不只是比较底层模型**。

## ✨ 你会得到什么？

- **智力测评**：测试推理、指令理解、事实可靠性与模拟任务处理。
- **专属报告**：能力分数、擅长领域、薄弱环节和趣味“虾格”称号。
- **有据可查**：自动生成题目、程序验分、保留可复核的测试结果。

## 🦞 面向哪些龙虾？

| 对象 | 代表项目 | 当前方式 |
| --- | --- | --- |
| **OpenClaw** | [OpenClaw](https://github.com/openclaw/openclaw) | 已提供 CLI 自动测评及手动答卷导入 |
| **其他 Claw 智能体** | [NanoClaw](https://github.com/nanocoai/nanoclaw)、[ZeroClaw](https://github.com/zeroclaw-labs/zeroclaw)、[PicoClaw](https://github.com/sipeed/picoclaw)、[IronClaw](https://github.com/nearai/ironclaw)、[MicroClaw](https://github.com/microclaw/microclaw) | 使用通用答卷导入；各自的自动适配尚未实现 |
| **其他 AI 智能体** | [nanobot](https://github.com/HKUDS/nanobot) 及能回答文本题目的 Agent | 使用通用答卷导入；自动适配待开发 |

以上是**目标适用范围**，不是已全部通过自动集成测试的兼容清单。

## 🚀 快速开始

在项目目录运行，要求 Python 3.10+：

```bash
# 离线查看演示报告：不调用任何真实 AI
python -m clawiq demo --suite quick --out ./demo
# 打开 ./demo/report.html
```

已经配置 OpenClaw 的用户，可先检查 CLI，再启动真实测评：

```bash
python -m clawiq doctor
python -m clawiq run --suite quick --out ./my-lobster --ack-provider-calls
# 打开 ./my-lobster/report.html
```

其他龙虾可通过 `generate → 提交答卷 → score` 完成测评。具体步骤见 [使用说明](docs/USAGE.md)。

## 📌 当前版本

**V0.1.1 · 12 题体验版 / 40 题标准版。** 当前测试范围是认知题与文字模拟任务，尚未完成真实外部工具调用、跨会话记忆、训练效果的正式测评；OpenClaw 自动模式已通过 CLI 接口测试，尚未验证真实用户的模型环境。真实模型调用可能产生费用。

趣味分数**不等于人类 IQ**，也不用于权威排名；共享报告前请检查敏感内容。

[体验报告 HTML](web/report-preview.html) · [详细使用](docs/USAGE.md) · [测评方法](docs/METHODOLOGY.md) · [隐私与安全](docs/SECURITY.md) · [验收记录](docs/VALIDATION.md)

MIT 开源 · 非任何上述智能体项目的官方产品。
