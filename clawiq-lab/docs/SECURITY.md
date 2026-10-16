# 安全与隐私边界

ClawIQ V0.1 属于个人自测工具，不可视为安全沙箱或作弊防护系统。

- **禁止将答案给被测龙虾**：`answer-key.private.json` 放在考官本机输出目录，权限尽力限制为0600；题目文本不含答案。
- **默认无网络**：`generate`、`demo`、`score`、`verify`、`render` 使用 Python 标准库，不调用第三方模型服务。用户执行 `run --ack-provider-calls` 才会真正调用 OpenClaw 配置的模型，可能产生费用。
- **外部能力隔离**：OpenClaw `agent exec` 自建临时状态、独立工作目录，强制 `minimal` 工具档、禁止 gateway 工具、`direct` 模式。用户已有插件、原生运行时、凭证环境、宿主机权限仍可能带来差异，不能视为操作系统级沙箱。严格敏感环境应在无私人数据的独立容器/虚拟机执行。
- **有限操作**：不要求龙虾执行 Shell、删除文件、发送消息或访问账号；所有任务数据均为生成的合成文本。
- **共享前检查**：`responses.private.json` 可能含模型原始文本，不应公开。报告 `report.json`/`report.html` 默认只包含合成题、标准答案、结构化观察（错误结果可保留简化描述）；公开分享前仍应人工复核。
- **不可防作弊**：开源 Python 生成器在本地可再生成答案。任何人均可打开私有答案文件，不能用于付费认证或可信全球排名。
- **限制成本**：体验版12轮、标准版40轮。项目自身不持有 API 密钥；OpenClaw 配置可能在环境中提供付费模型凭证。每题超时默认120秒；失败即停止。
- **版本验证**：兼容入口来源是 OpenClaw 文档 `docs/cli/agent.md` 所述 `openclaw agent exec`，而不是所有已发行历史版本。部署前应本地检查实际 CLI 版本与工具策略行为。

- **真实 Agent 模式**：`--backend gateway` 同时需要 `--ack-provider-calls --allow-existing-tools`。此模式访问用户已有 Gateway、现有 Skill/记忆/工具并创建持久会话；没有运行时沙箱保证，必须由主人明确授权并仅在最低权限环境运行。与默认的 `isolated` 模式严格区分。
