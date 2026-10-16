# ClawIQ Lab · 详细使用说明

本页保留完整操作手册。**仅 OpenClaw 提供自动测评命令**；NanoClaw、ZeroClaw、PicoClaw、IronClaw、MicroClaw、nanobot 等目前通过通用答卷导入方式参与测评。不能将手工导入称为官方兼容验证。

---

# 🦞 ClawIQ Lab · 龙虾智力评测

**给自己养的 OpenClaw 做一次有证据的“智力体检”。**

> 你养的龙虾有多聪明？擅长推理还是细节执行？当信息缺失时它会承认不知道吗？ClawIQ Lab 用动态合成题目、客观判分和漂亮的本地报告，帮助主人认识自己养的智能体。

**项目状态：V0.1.1 可运行开源 MVP（新增 CLI 预检与无工具脑力测试加固）。** 它不是标准人类 IQ 测验，也不是正式科学认证或 OpenClaw 官方产品。首次发布以**认知能力 + 模拟工作任务**为范围，暂不声称覆盖真实工具调用、跨会话记忆或完整的训练闭环。

## ✨ 能做什么？

- 🧠 **测脑力**：逻辑推理、复杂指令、证据充分性判断，题目根据随机种子生成。
- 🧰 **测模拟任务**：以合成订单和虚拟依赖任务评估工作处理能力，不碰真实私有文件。
- 🔎 **客观评分**：逐题标准答案、严格 JSON 判分、原始答复私有留存、结果复核。
- 🦞 **专属虾格**：根据本次相对优势给出“规律探索虾 / 细节执行虾 / 谨慎求证虾 / 任务规划虾”称号；不是人格科学分类。
- 🎴 **趣味报告**：支持离线 HTML 展示、导入本地 JSON、打印 PDF，页面无云端依赖。
- 🛡️ **可控接入**：Python 标准库核心、外部模型调用需显式确认；不修改现有 OpenClaw 的长期配置和记忆。

## 🚀 立即体验

要求 Python 3.10+，**离线演示不需要 OpenClaw、API Key 或付费服务**。

```bash
# 在本项目目录下
python -m clawiq demo --suite quick --out ./my-demo
# 打开 my-demo/report.html 查看演示报告
python -m clawiq verify ./my-demo
```

`demo` 由程序自己提供模拟答案，报告会明确标记 **DEMO / 非真实模型测试**。这只能验证整套出题与评分管线是否工作，不能作为龙虾成绩。

### 给自己安装的 OpenClaw 做真实问答测评

开始之前先运行以下只读预检（不会调用付费模型）：

```bash
python -m clawiq doctor
```

如果 CLI 版本不支持必要参数，`run` 会在创建任何测评文件前停止。


要求本机 `openclaw` 命令可用、已配置模型；每题执行一次隔离的 `openclaw agent exec`。模型提供商可能按调用量收费，**命令必须加入显式授权参数**：

```bash
python -m clawiq run --suite quick --label "我的龙虾" \
  --out ./my-first-test --ack-provider-calls
python -m clawiq verify ./my-first-test
# 打开 ./my-first-test/report.html
```

标准版需额外调用（40道题而不是12道），请先在自己配置环境上完成体验版并核对费用：

```bash
python -m clawiq run --suite standard --seed 20261017 \
  --label "我的龙虾" --out ./my-standard-test --ack-provider-calls
```

运行方式遵循 OpenClaw 2026 年 `agent exec` CLI：临时工作目录、一次性状态、`--code-mode direct`、临时 `tools.deny=["*"]` 阻止全部模型工具，并关闭自动工作空间上下文注入。该设置意在减少测试带来的额外权限暴露，**但不能证明底层所有插件/运行时完全沙箱隔离**；有严格隐私或安全要求时，应在独立测试机器或容器运行。

此外，本模式衡量的是 OpenClaw 通过受限一次性会话对合成题的回答表现，不等于对日常启用的所有 Skills、记忆和工具配置进行端到端测量。相关专项测试是下一阶段计划。

### 可选：测自己已经配置的完整龙虾（Gateway 模式）

可先执行 `python -m clawiq doctor --backend gateway` 核对 CLI 功能；这不会连接 Gateway 或调用模型，也不代表真实服务已经连通。

前述 `run` 默认是**隔离模式**：测试当前 OpenClaw 配置所使用的模型/运行时，但不继承主人日常聊天的完整记忆、会话和工具环境。若希望观察**已经养成的智能体**在其实际 Gateway 配置下的回答，可显式选择：

```bash
python -m clawiq run --backend gateway --agent-id main --suite quick \
  --label "我的龙虾" --out ./my-live-lobster --ack-provider-calls --allow-existing-tools
```

**风险提示：此模式会创建持久会话，并使用已有 Agent 的 Skill/记忆/工具权限，可能触发真实工具行为、网络请求与费用；本项目无法在客户端替你收回这些权限。** 仅在你信任的、已最小权限配置的测试 Agent 上执行，最好使用专门的测试环境。ClawIQ 问题本身只包含合成文本，不主动要求读取私人资料或执行外部操作，但不能保证智能体或插件不自行调用工具。报告会注明 `openclaw-gateway`。

### 给任意其他 AI 做手工测评

先生成问卷；**不要把 `answer-key.private.json` 提供给被测 AI**：

```bash
python -m clawiq generate --suite quick --seed 42 --out ./exam-42
```

每题给 AI 发送 `form.public.json` 中的 `prompt`，按顺序保存 `responses.json`：

```json
[
  {"id": "从表单复制的题目ID", "raw": "{\"answer\":123}"}
]
```

提供**全部题目**的 `{id,raw}` 后评分：

```bash
python -m clawiq score --form-dir ./exam-42 \
  --responses ./responses.json --out ./my-manual-result --label "龙虾A"
python -m clawiq verify ./my-manual-result
```

测试人能看到本地答案文件，适合自测和内部比较，**不具备防作弊认证能力**。

## 🧭 How it works / 测评流程

```text
出题器（公开题目 + 本地私有答案）
       ↓
被测龙虾（OpenClaw 一次性最小权限会话）
       ↓
独立判分器（程序逐题匹配 JSON 标准答案）
       ↓
报告（脑力分、模拟任务分、优弱项、案例、可复核记录）
```

| 维度 | 体验版 | 标准版 | 被测能力 |
|---|---:|---:|---|
| 逻辑推理 | 4 | 12 | 数学递推与多条件运算 |
| 理解与遵循 | 3 | 10 | 合成数据筛选、排序与格式遵循 |
| 事实可靠性 | 3 | 10 | 有证据、无证据、冲突信息的判断 |
| 模拟任务执行 | 2 | 8 | 虚拟资料处理和依赖规划 |
| **合计** | **12** | **40** | 两档均为探索性产品测评 |

**评分公式（V0.1）**：脑力分 = 45% 推理 + 30% 指令 + 25% 可靠性；模拟任务分 = 模拟任务正确率；综合分 = 60% 脑力 + 40% 模拟任务。所有分数均为 0–100 产品内指标，**无基于人类群体的 IQ 转换、无同类排名校准**。体验版由于题少尤其不适合横向排名。

## 📦 包结构

```text
clawiq/                Python 出题、校验、OpenClaw 接入与报告模块
skill/clawiq-lab/       可复用的 SKILL.md 操作说明（供测评操作者使用）
web/report.html         单文件离线报告模板，支持导入 JSON
web/report-preview.html 演示报告，可直接打开
examples/               虚构报告示例（明确 DEMO）
tests/                  unittest 测试
docs/                   方法、权限边界、验证记录、计划
```

## 🔒 隐私与安全

- **离线 demo 不发生网络调用。** `run` 必须由操作者显式加 `--ack-provider-calls`，请求次数取决于选择的题量。
- 不向测试题提供真实邮件、文档、密码或私人会话；仅合成数据。
- 私有答案和模型原始响应默认存储为本地 `*.private.json`，不会自动上传。
- 错题诊断证据使用题目、预期答案和错误类型；不在分享报告中直接暴露未知的模型原文。
- 输出文件不可用于对外认证或跨配置公平排名。GitHub 仓库只包含**合成演示报告**。

参见 [安全边界](docs/SECURITY.md) 和 [测试方法](docs/METHODOLOGY.md)。

## 🧪 验证

```bash
python -m unittest discover -s tests -v
python -m compileall -q clawiq tests
```

已执行测试摘要见 [docs/VALIDATION.md](docs/VALIDATION.md)。当前运行环境无法实测用户自己的 OpenClaw，因此**正式 Agent + 服务商调用保留为待验证**，不冒充已通过的集成测试。

## 💡 为什么做 ClawIQ？

参考 [AI IQ (fun)](https://github.com/epoko77-ai/ai-iq-test) 的可核查合成题与趣味呈现、[ClawGym-Bench](https://github.com/ClawGym/ClawGym-Bench) 的任务验证思路、[SkillsBench](https://github.com/benchflow-ai/skillsbench) 的测评实践。V0.1 所有测试逻辑与 UI 为独立原创实现；**未复制这些项目的题库或代码**。

与大模型排行榜不同，我们关注**主人养成的一个具体智能体配置**。后续的价值不在于制造一个吸睛数字，而是让用户有证据地发现强项与弱项，并能够验证下一次改进。

## 🤝 贡献与路线图

欢迎报告误判、贡献能程序校验的新题型、帮助进行不同 OpenClaw 版本的实际兼容性验证。优先阅读 [路线图](docs/ROADMAP.md)。涉及真实工具调用或跨会话记忆的提案，需同时提供隔离执行和防数据泄露的策略。

开源协议：MIT，见 [LICENSE](LICENSE)。独立社区项目，与 OpenClaw 官方无隶属关系。



## OpenClaw 2026.10.2：显式最小配置模式

该固定版本只有 `--config`，没有 `--config-override`。使用新增 `--model provider/model`，ClawIQ 生成经该版本 schema 校验的最小配置，不导入原有配置、插件或凭据存储；缺少模型参数时会明确失败，不降级到不受限运行。支持 override 的版本原有用法保持不变。

```bash
# 仅参数检查，不调用模型
python -m clawiq doctor --model openai/YOUR_MODEL
# 用户确认费用后自行运行；只转交明确选择的环境变量
python -m clawiq run --model openai/YOUR_MODEL --provider-env OPENAI_API_KEY --suite quick --out ./explicit-test --ack-provider-calls
```

模型名必须替换为服务商实际支持的模型。凭据由用户在自己的环境设置，不放入本项目文件、命令参数或报告。允许的变量名为 OPENAI_API_KEY、ANTHROPIC_API_KEY、GEMINI_API_KEY、GOOGLE_API_KEY；其他鉴权方式暂不支持此模式。每题使用临时 HOME/state、禁插件、禁全部工具、禁止上下文自动注入、关闭 shell 环境导入；只保留运行所需 PATH/SYSTEMROOT 与明确选择的提供商变量。原始回答仍私有保存。

报告模式为 `openclaw-exec-config`，应与继承用户配置的测评区分；它不测量用户的已有 Skills/记忆/模型运行时配置。缺少零工具调用回执时失败，不给有效分数。临时目录是进程级隔离，不是操作系统或网络沙箱；真实运行需要访问选择的模型提供商，可能收费。当前证据只有官方 CLI 帮助/schema 校验和模拟进程测试，真实模型与工具拒绝端到端尚未验证。
