# 长期主义协作原则包

Codex Longterm Collaboration Principles

版本：v1.1  
日期：2026-06-11

## 简介

这是一个面向 Codex 和其他代码协作代理的场景化原则包。它把“整体原则”拆分为总控入口、场景路由、产品研发、产品变现、日常工作、代码开发、文档沉淀、交付检查和变更日志规则，让代理在不同任务里稳定调用对应规则，而不是把所有原则混在一起无差别执行。

v1.1 引入 Skill 化增强：明确触发条件、不适用场景、任务启动规程、协作收口模板、复核点和轻任务免打扰规则。

推荐 GitHub 仓库名：

```text
codex-longterm-collaboration-principles
```

## 适合场景

- 产品研发与原型开发
- 功能必要性判断
- 产品商业化与变现判断
- 日常工作流程、汇报、协作和风险判断
- 代码修改、测试和交付说明
- 文档、规则库、版本迭代与变更日志

## 不适合场景

- 简单事实问答、单步解释、错别字修正等轻任务。
- 用户明确要求只给结论、不要展开流程。
- 已有更高优先级的专用 Skill 或工具规则，例如表格、文档、PPT、浏览器测试。
- 缺少基本事实时，不应强行判断，应先列出调查清单或确认问题。

## 目录结构

```text
AGENTS.md                         # 总控入口，放在项目根目录
agent-rules/                      # 场景化规则模块
templates/                        # 常用判断模板
commands/                         # 可选调用模板
codex-skill/                      # 可安装到 Codex 的入口型 Skill
source/                           # 原始原则和旧版变更日志备份
AGENTS_单文件版_SingleFile.md      # 可直接粘贴使用的单文件版
README_使用说明_Usage.md           # 原始使用说明
MANIFEST_文件清单.md               # 文件清单
PrincipleChangeLog.md             # 当前变更日志
VERSION                           # 版本信息
```

## 推荐使用方式

把以下内容复制到你的项目根目录：

```text
AGENTS.md
agent-rules/
templates/
```

之后在 Codex 中打开该项目时，优先让它读取根目录的 `AGENTS.md`。`AGENTS.md` 会作为总控入口，要求代理根据任务类型读取对应模块。

## Codex Skill 使用

如果想作为用户级 Codex Skill 使用，可以把以下目录复制到你的 Codex skills 目录：

```text
codex-skill/interaction-principles/
```

推荐调用语：

```text
启用交互原则
Use $interaction-principles to apply the longterm collaboration principles.
```

该 Skill 是入口型 Skill：它不复制全部模块内容，而是要求代理优先读取项目里的 `AGENTS.md` 和对应 `agent-rules/` 模块。这样 GitHub 包保持为主版本源，本地 Skill 负责稳定触发。

## 可选命令模板

`commands/启用长期主义协作_LongtermCollaboration.md` 可作为 slash command 或 prompt 模板使用。它会要求代理读取 `AGENTS.md`，完成场景路由，并在复杂任务末尾做协作收口。

## 单文件使用

如果暂时不想管理多个文件，可以直接使用：

```text
AGENTS_单文件版_SingleFile.md
```

单文件版适合快速粘贴，模块化版本更适合长期维护。

## 维护原则

- 通用原则只放在 `agent-rules/00_总体原则_OverallPrinciples.md`。
- 场景规则只放在对应模块。
- 检查清单只放在 `agent-rules/07_交付检查_Checklists.md`。
- 版本与变更规则只放在 `agent-rules/08_变更日志_ChangeLogRules.md`。
- 新增或修改规则时，同步更新 `PrincipleChangeLog.md`。

## v1.1 核心增强

- 轻任务免打扰：小任务直接完成，不强行套完整流程。
- 任务启动规程：判断场景、校准主目标、设定成功标准、选择输出形态。
- 决断收口：复杂任务补充当前判断、把握度、下一步最小动作、最坏风险和复核点。
- 交付收口模板：避免只写“已测试”，必须说明具体检查链路。
- Codex Skill 入口：新增 `codex-skill/interaction-principles`，便于在本机稳定触发。


## 🦞 独立开源子项目

- [ClawIQ Lab · 龙虾智力研究所](clawiq-lab/README.md)：专门为自己养的 OpenClaw 智能体提供合成题智力测评、独立评分、趣味报告与可复核记录。代码、Skill、测试及 HTML 均在 `clawiq-lab/` 目录，MIT 开源。
