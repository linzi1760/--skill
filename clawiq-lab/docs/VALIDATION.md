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
