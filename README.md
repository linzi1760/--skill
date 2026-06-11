# 长期主义协作原则包

Codex Longterm Collaboration Principles

版本：v1.0  
日期：2026-06-11

## 简介

这是一个面向 Codex 和其他代码协作代理的场景化原则包。它把“整体原则”拆分为总控入口、场景路由、产品研发、产品变现、日常工作、代码开发、文档沉淀、交付检查和变更日志规则，让代理在不同任务里稳定调用对应规则，而不是把所有原则混在一起无差别执行。

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

## 目录结构

```text
AGENTS.md                         # 总控入口，放在项目根目录
agent-rules/                      # 场景化规则模块
templates/                        # 常用判断模板
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
