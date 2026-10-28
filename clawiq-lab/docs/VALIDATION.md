# V0.1 实测与验收记录

执行日期：2026-10-16（本地构建环境）

## 运行命令与实际结果

```bash
python -m unittest discover -s tests -q
# Ran 26 tests ... OK
python -m compileall -q clawiq tests
# 成功，退出码 0
python -m clawiq demo --suite quick --out ./_example_tmp
python -m clawiq verify ./_example_tmp
# VERIFIED，12题（演示模拟答复）
```

## 覆盖范围

- `core`：seed 重现、种子不同试题差异、题型及题数、题目与答案隔离、篡改答案拒绝、非法参数拦截。
- `scoring`：四维全部通过、严格类型比较、错误 JSON 判错、缺题/重复 ID 拒绝、提供商错误令报告无效、报告篡改复核失败、未知原文不泄漏到公共报告。
- `runner`：`agent exec --json` JSON 提取、失败拦截、最小权限标记、缺少 CLI 报错；Gateway 模式参数与响应结构模拟验证；明确调用授权门槛。
- `CLI + HTML`：离线 demo → verify → render、生成 → 手工答复 → score → verify、禁止覆盖原输出、HTML 脚本注入内容转义。

## 没有验证的事情

- 当前容器没有实际连接用户的 OpenClaw Gateway 或付费模型，不存在“真实龙虾测评通过”结论。
- OpenClaw CLI 不同历史版本的响应结构和配置项兼容性未做真实跨版本测试。
- 用户本地浏览器（尤其移动端）尚未完成视觉截图回归；静态 HTML 文件不等于经过浏览器自动化测试。
- 没有进行外部专业测量效度校准；12/40题不能用于准确的 AI IQ 排名。

## 判定

**通过：离线出题、客观判分、私有记录复核、HTML 生成、外部调用授权门槛的自动化测试。**

**待验证：真实 OpenClaw/模型端到端兼容、不同配置比较、真实工具调用、跨会话记忆、浏览器实测。**

## V0.1.1 进程级集成模拟与兼容性（2026-10-16）

- 新增 `doctor` CLI 预检，验证必要参数存在且不触发模型调用。
- 强化独立脑力测评临时配置，禁止全部模型工具，禁止自动注入工作空间上下文。
- 新增测试：模拟 `openclaw` 可执行文件，实际执行12题流程、评分、报告复核；模拟违规工具调用时应停止且只留私有检查点；缺失 CLI 时不创建空成绩目录。
- 进程级测试属于**模拟验证**，不能替代真实 OpenClaw 服务商端到端验收。
- 实际通过/失败状态以此版本对应的 GitHub Actions CI 结果为准。


## 2026-10-16 独立复验：模块退出码与真实 CLI 阻塞

- 基线：`a3d702a04f9d0c8071b7e8f85878076339800909`，Python 3.12.14。
- 31 个原有离线测试通过；quick 12 题及 standard 40 题 demo → verify 均通过。
- 发现 `python -m clawiq` 丢弃 main 返回值：缺少调用授权、缺少 CLI 等错误退出为 0。修正为 `raise SystemExit(main())`，加入四个真实 Python 子进程回归，35 个测试通过；compileall 通过。
- **撤回“绿色 CI 即证明 isolated CLI 兼容”的推断**：[基线真实 CLI 日志](https://github.com/linzi1760/--skill/actions/runs/38925522644/job/117055947110) 显示 OpenClaw 2026.10.2 缺少 `--config-override`。旧入口把此错误吞成退出码 0；Gateway doctor 的参数检查通过。
- 本修复不移除安全配置，也不伪造兼容通过。隔离模式的配置接口需按固定版本官方实现修复并重新验收。
- 未调用真实模型、用户 Gateway 或收费 API；未验证真实工具和跨会话记忆；未做浏览器视觉回归。

## 显式配置候选复验

- 官方 OpenClaw 2026.10.2：无凭据、临时 HOME/state 下 `config validate --json` 返回 valid:true/warnings:[]，`agent exec --help` 包含 --config。证据：https://github.com/linzi1760/--skill/actions/runs/38927334531/job/117062122357 。
- 本地 Python 3.12.14：40 个测试通过；新增参数拒绝、环境白名单、配置不含凭据/禁止插件与工具、临时文件权限和清理、缺失工具回执拒绝、12题模拟进程→verify。compileall 通过。
- 模式为新增显式接口；旧 override 模式保留。只支持列明的环境变量 API key，不自动读取存储登录或用户配置。固定 CLI 的默认无模型命令仍有意失败，并提示显式模型参数。
- 不代表模型请求成功、真实工具防护生效、跨会话记忆或浏览器验收通过。

## 2026-10-28 隔离工具回执失败关闭复验

- 基线：PR #5 head `259254c1cefb4565b10b7ba55de7c78d9b685400`。该 head 的 3 项 CI 仍为 success；PR 保持 draft/open，未合并或部署。
- 独立复现：旧 override 路径将 `toolSummary=null` 或 `{}` 当作可接受的无工具结果；显式 config 路径已有额外门禁，旧路径没有。已将必要回执检查移至共同提取入口。
- 新行为：所有隔离模式必须收到 `toolSummary.calls` 为整数 `0`，缺失或类型不明确即拒绝。Gateway 不受此无工具约束影响，也不因此取得任何新增授权。
- 本地 Python 自动化：42 项离线测试通过，compileall 通过；其中 2 项新增回归覆盖缺失/畸形工具回执及旧 override 调用路径。模拟进程仍明确属于模拟。
- 本地已有 Codex CLI `0.166.0-alpha.1`，原生 `codex login status` 返回 ChatGPT 登录。受控 ephemeral 调用在 app-server 初始化阶段因只读文件系统失败，未出现 thread/turn 事件，未取得模型答复。不得把登录状态当作实际推理通过。
- 未读取/复制凭据、未购买 API 额度、未新增登录、未访问用户电脑。未验证 OpenClaw 模型链路、真实工具拒绝或跨会话记忆。

### 原生模型实答 → 通用导入链路（不是 OpenClaw 验收）

- 采用新的无历史继承原生子代理，传入 seed `20261028` 的 12 道公开题目；没有传入答案键。代理返回的原始 JSON 答卷保留在本地私有证据中。
- 这是同一批次中的 12 题，不是 12 个隔离模型会话。提示要求不调用工具，但没有取得可独立审计的运行时工具拒绝回执；不据此宣称工具隔离生效。
- 原有 `score → verify` 实际完成：`mode=manual-import`、`demo=false`、`status=complete`、`sample_size=12`，12/12 答案符合预先生成的确定性标准，总分 100。仅证明本次实答导入、客观评分和报告复核链路完成，不代表广泛能力排名或人类 IQ。
- 原生子代理由当前任务平台运行；没有独立服务商用量/计费或模型版本回执，不把其标作指定模型、付费 API、OpenClaw 或 Codex CLI 的执行结果。
- 浏览器验收未完成：云容器 Chromium 启动被 socket 权限限制阻断，云浏览器不允许 `file://` 协议。没有页面功能或移动端视觉通过结论。
- 尚未达到完整上线标准：真实 OpenClaw 自动测评、工具拒绝端到端、跨会话记忆及实际浏览器交互仍需可用且授权的对应运行环境。

- 解释限制：本次四维均为 100%，现有报告按排序规则仍会显示一个“强项/短板”标签；这不是实测发现了能力短板，不能将该同分标签解读为真实优劣。
