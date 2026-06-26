# plan — Phase 0 平台机制 spike

> 工作艺术品，非设计文档。落地 [roadmap](roadmap.md) 的 Phase 0：七条平台机制
> spike 拿 **yes/no + 投递决策**，归 `experiments/`，门禁 Phase 3/5/6 的 live 与投递
> 形态。不进 CI。

## 范围与证据基准

平台机制（Claude Code 的 plugin/agent/MCP/hook/transcript 行为）不能单测，必须落到真
宿主结论。两类证据基准，每条卡标明：

- **doc-confirmed** —— 官方 docs（`code.claude.com/docs`，版本对齐 2.1.x），原文 + URL。
  文档化的能力契约，权威即结论。
- **host-observed** —— 真 transcript / 本会话实测，`probe.py` 可复跑。

只钉**能力/契约**。**行为质量型** live（reflector compare-first 真改优于建、PreToolUse
运行时真 deny 一次 `Write`）属 Phase 5 live 测试，不在 Phase 0。

## 七条结论（详见证据卡）

| spike | 问题 | 结论 | 投递决策 | 卡 / 基准 |
|---|---|---|---|---|
| S1 | plugin 装的 agent 支持 `hooks`/`mcpServers` frontmatter？ | **否**（安全，2.1.63+ 忽略） | reflector backstop + stage_skill 注册**退到 plugin 顶层** | E6 / doc |
| S2 | MCP 能 scope 到单 subagent？ | **能**（inline frontmatter），但 plugin agent 忽略该字段 | stage_skill 走 plugin `.mcp.json`（会话可见；land 确定性独占，非安全洞） | E6 / doc |
| S3 | subagent 自身 PreToolUse 生效？deny 协议？ | **生效**；deny=exit 2 或 JSON `permissionDecision:deny` | 顶层 PreToolUse 按 `agent_type` 匹配 reflector，挡 `Write`/`Edit` | E6 / doc |
| S4 | 省略 `tools` 全继承？`plugin:reflector` 可解析？ | **是**；`plugin:agent` 可解析；SubagentStop≠Stop | reflector 仍用显式最小工具集；CAP 只数主 `Stop` | E6 / doc |
| S5 | learned skill 走 `Skill` 工具 + 带符号身份？ | **是**；transcript 另记 `attributionSkill`（带命名空间） | MNG 率**分子**有真符号 hook | E6 / doc+host |
| S6 | `Stop` ↔ API 请求一一对应？ | **每 turn 一次**；一 turn 内多次 requestId | MNG 率**分母 = per-turn/per-Stop**，非 per request | E6 / doc+host |
| S7 | session-id→transcript 发现？compaction 下 tail-N 取原始轮？ | **都 yes**：路径 `<sessionId>.jsonl` 确定；compaction 只追加 summary、不删原始轮 | CAP 读文件取 tail-N，不受 compaction 影响 | E5 / host |

## 落位

- `experiments/E5_transcript_discovery/`（S7，host）—— `probe.py` + `results.md`。
- `experiments/E6_platform_contracts/`（S1–S6，doc + host 交叉验）—— `probe.py` 复跑
  S5/S6 的可观测部分；S1–S4 与 deny 协议由 `results.md` 携 docs 原文 + URL。

## 决策待吸收进设计文档（建 Phase 3/5/6 时）

spike 决策现住证据卡，建对应 Phase 时落进权威设计文档：

- [mng](../research-loom/design/mng.md)：率分母粒度锁 per-turn/per-Stop（S6）；分子取
  `PreToolUse(Skill)` 的命名空间 skill id（S5）。
- [reflector-subagent](../research-loom/design/reflector-subagent.md) /
  [architecture](../research-loom/design/architecture.md)：backstop = plugin 顶层
  `hooks.json` 按 `agent_type` 匹配（S1+S3）；reflector 显式最小工具集（S4）。
- [stage-skill](../research-loom/design/stage-skill.md)：stage_skill 走 plugin
  `.mcp.json`、会话可见可接受（S1+S2）。
- [cap](../research-loom/design/cap.md)：只数主 `Stop`，reflector 完成是 `SubagentStop`
  不入分母（S4）；tail-N 直读 `.jsonl`（S7）。
