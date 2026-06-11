# Codex 场景化总体原则包 / Codex Scenario Rules Pack

版本 / Version：v1.0  
日期 / Date：2026-06-11

## 这个包解决什么问题

这个包用于让 Codex 或其他代码协作代理在不同任务场景下稳定调用对应规则，而不是把所有原则混在一起无差别执行。

核心结构是：

```text
AGENTS.md                         ← 总控入口，放在项目根目录
agent-rules/                      ← 场景化规则模块
  00_总体原则_OverallPrinciples.md
  01_场景路由_ScenarioRouter.md
  02_产品研发_ProductDevelopment.md
  03_产品变现_ProductMonetization.md
  04_日常工作_DailyWork.md
  05_代码开发_CodeDelivery.md
  06_文档沉淀_DocumentationRules.md
  07_交付检查_Checklists.md
  08_变更日志_ChangeLogRules.md
templates/                        ← 常用判断模板
source/                           ← 原始原则备份
```

## 推荐使用方式

把以下内容复制到你的项目根目录：

```text
AGENTS.md
agent-rules/
templates/
```

之后在 Codex 中打开该项目时，优先让它读取根目录的 `AGENTS.md`。  
`AGENTS.md` 会作为总控入口，要求代理根据任务类型读取对应模块。

## 单文件使用方式

如果你暂时不想管理多个文件，可以直接使用：

```text
AGENTS_单文件版_SingleFile.md
```

这个文件把所有模块合并成一个可粘贴版本。缺点是后期维护不如模块化结构清楚。

## 适合的任务类型

- 产品研发与原型开发
- 功能必要性判断
- 产品商业化与变现判断
- 日常工作流程、汇报、协作、风险判断
- 代码修改、测试、交付说明
- 文档、规则库、版本迭代与变更日志

## 基本调用逻辑

每次任务开始时，代理应该先执行：

1. 读取 `AGENTS.md`。
2. 读取 `agent-rules/00_总体原则_OverallPrinciples.md`。
3. 按任务关键词和意图读取对应场景模块。
4. 如果涉及交付，读取 `agent-rules/07_交付检查_Checklists.md`。
5. 如果涉及规则、文档、原型、关键功能变化，读取 `agent-rules/08_变更日志_ChangeLogRules.md`。

## 维护原则

- 通用原则只放在 00 模块。
- 场景规则只放在对应模块。
- 检查清单只放在 07 模块。
- 版本与变更规则只放在 08 模块。
- 新增规则时同步更新变更日志。
