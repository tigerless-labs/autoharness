# plan — Phase 7：plugin 打包 + 单 dispatcher + marketplace + 端到端

> 工作艺术品（非设计文档）。装配自 [roadmap](roadmap.md) Phase 7 + [architecture](../research-loom/design/architecture.md)
> + Phase 0 平台契约（[E6](../../experiments/E6_platform_contracts/results.md) S1–S6 已闭）。每单元 docs→tests→code、tests 先于 code。

## 范围

把 Phase 1–6 的确定性件接成可安装 plugin。**确定性那半全进 CI**（dispatch 路由 + 清单结构 + serve JSON-RPC + config env-override），**活宿主那半留 `experiments/` runbook 骨架 + `@pytest.mark.live`**（真装 / 真召回 / 真 spawn）。

S1–S6 已闭（E6），据此定投递：backstop 与 stage_skill **退到 plugin 顶层**（agent frontmatter 不认 hooks/mcpServers）；deny=exit2 / stdout JSON；Skill 用走 `PreToolUse(Skill)`、身份在 `tool_input`；`Stop`=每回合 → 分母在 Stop +1（补 Phase 6 缺口：现无人 +1 分母 → 全员永久缓刑）。

## 单元

### U1 docs — 吸收 S1–S6 投递决策
- `reflector-subagent.md`：backstop 从「subagent frontmatter 自带 hooks」改为 **plugin 顶层 `hooks.json` PreToolUse 按 `agent_type` 匹配 deny `Write`/`Edit`**（S1 否定 agent 自带 hooks）。
- `architecture.md`：确认 dispatch 单入口 + hooks.json/.mcp.json 顶层注册；记**每回合分母 +1 在 `Stop` 经 dispatch**（S6）、SubagentStop 不计（S4）。
- TODO：勾「吸收 Phase 0 决策」「stage_skill MCP 进程绑定接 Phase 7」「spawn host-detach 接 Phase 7」。

### U2 tests+code — `config` env-override（runbook 调小旋钮的前提）
- `REFLECT_EVERY_N` / `MATURITY_THRESHOLD`(两层) / `CAPACITY`(两层) 读 `AUTOHARNESS_*` env、缺省回现值。
- test：set env + reload → 覆盖生效；不设 → 缺省；断言关系（>0、两层俱在）。

### U3 tests+code — `hook/dispatch.py` 单入口路由
- 解析 `hook_event_name` → 路由：`SessionStart`→on_session_start；`Stop`→**分母两层 bump_request** + on_stop（触发则物化窗 + detached spawn launcher，可注入）；`SessionEnd`→on_session_end（触发则同）；`PreToolUse`：`tool_name==Skill`→on_skill_call、reflector `agent_type` + `Write`/`Edit`→**deny**；`SubagentStop` / 未知 → 安全忽略。
- 全程 fail-safe：handler 抛异常不崩宿主 hook（吞错、退安全 ignored）。
- test（unit，喂 event dict）：每事件→正确 handler（注入桩/launcher）；Skill 计分子；reflector Write→deny verdict；未知忽略；Stop 两层分母 +1；触发→launcher 调；handler 异常被吞。

### U4 tests+code — `stage_skill/server.py` 的 stdio MCP `serve()`（零依赖）
- 加 JSON-RPC 2.0 处理器 `handle(request)`：`initialize` / `tools/list`（吐 TOOL_SCHEMA）/ `tools/call`（调 `stage()`，run_id/root 经 env 注入）；`serve()` 行分隔读写 stdin/stdout。**禁引 mcp SDK**。
- test：initialize→capabilities；tools/list→含 stage_skill schema；tools/call→append 队列且回 result；未知 method→JSON-RPC error；通知（无 id）不回。

### U5 tests+code — plugin 清单 + marketplace
- `.claude-plugin/plugin.json`、`hooks/hooks.json`（事件→`PYTHONPATH=${CLAUDE_PLUGIN_ROOT}/src python3 -m autoharness.hook.dispatch`，PreToolUse 含 Skill + reflector 写 backstop）、`.mcp.json`（stage_skill serve）、`.claude-plugin/marketplace.json`（单 plugin、本仓即可 `/plugin marketplace add`）。
- test（结构）：四清单合法 JSON；hooks.json 各事件命令含 dispatch；.mcp.json 命名 stage_skill 且 args 含 server；plugin.json 有 name/version；marketplace.json 列本 plugin。

### U6 — 端到端 live runbook（不进 CI）
- `experiments/E7_end_to_end/`：runbook（隔离 HOME + 临时 repo + 本地装 plugin + env 调小旋钮 + 脚本会话 4 拍 + 盘上终态断言）+ `@pytest.mark.live` 骨架（标记跳过 / 记步骤）。归 evidence。

### U7 verify + sweep
- `pytest -m "not live"` 全绿；doc checkers 绿。扫 design/index.md。TODO 收尾。

## 留后（非本 Phase）
- 真活宿主 e2e 跑通（U6 runbook 执行）= Phase 0 行为验证 + 投递确认，人工 / 沙箱跑、记 evidence。
- detached 后台进程健壮性（孤儿、超时隔离）、transcript 上界 race 精确化留观测。
- 标定 config 默认值（experiments/）。

## 测试映射（roadmap 不变量）
- 「dispatch 路由（事件→on_*、未知忽略）」→ U3 unit。
- 「纯叠加、零侵入原生加载链」→ U3（dispatch 只调 handler、不碰 loader）+ U6 live。
- 「模型只 propose、land 确定性独占」→ U4（serve 只 append）+ promoter（已覆）。
- 「分母每回合 +1」→ U3（Stop 两层 bump_request），补 Phase 6 缺口。
