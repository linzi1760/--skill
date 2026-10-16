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
