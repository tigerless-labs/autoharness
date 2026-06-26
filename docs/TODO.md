# TODO — tracked follow-ups

> Smaller, uncommitted follow-ups and deferrals. Roadmap-level items belong in the design docs.
> Keep this current in real time: add on discovery, remove or check off on completion.

- [ ] **Measure interrogative-filter precision at scale** (Phase 2 entry). E2 sampled precision
  by hand (~5% → ~50%); needs a labelled measurement across projects under `experiments/`.
- [ ] **Locate the commit-signature instruction symbol.** E3's conflict case needs its source
  symbol identified (system prompt / settings / output-style) so Phase 0 can target the override.
- [ ] **Resolve the live signature conflict for this repo.** The harness instruction to add
  `Co-Authored-By: Claude` conflicts with the user's repeated correction (×11); decide retire vs
  hookify-override. Until resolved, this repo's own commits reproduce the flaw (see E3).
- [ ] **Decouple E1–E3 phrase lists into config.** The correction/theme phrase sets are inline in
  the experiment scripts; when the detector becomes product code it must move to config
  (`CLAUDE.md` "config holds every knob").
- [ ] **去重的触发时机:适配非常驻宿主.** Hermes 的 curator 靠常驻 daemon(空闲 2h / 间隔 7d 自动醒);
  Claude Code 等是临时进程,会话间无常驻、墙钟周期 sweep 无执行者。**失活已定**(MNG 走惰性 `SessionStart` 现算 +
  调用率判据,非墙钟刻度,见 [`research-loom/design/mng.md`](research-loom/design/mng.md));剩**去重走准入事件驱动**
  待落。见 [`research-loom/ideas/adherence-driven-curate.md`](research-loom/ideas/adherence-driven-curate.md) 的待解。
- [ ] **建 plugin 官方结构源卡**（`sources/`）：`plugin.json` / `hooks/hooks.json`（`${CLAUDE_PLUGIN_ROOT}` + `{"hooks":{...}}` 包裹）/ `agents/` / `.mcp.json` / marketplace —— `architecture.md` 的 provenance 现挂"待建"。
- [ ] **吸收 Phase 0 决策进设计文档**（建 Phase 3/5/6 时，决策现住 E5/E6 证据卡）：mng 率分母锁
  per-turn/per-Stop、分子取命名空间 skill id；reflector backstop=plugin 顶层 `hooks.json` 按 `agent_type`
  匹配；stage_skill 走 plugin `.mcp.json`；cap 只数主 `Stop`（reflector 完成是 `SubagentStop`）。见
  [`docs/plans/phase0-platform-spikes.md`](plans/phase0-platform-spikes.md)。
- [ ] **Phase 5 行为型 live**（非 Phase 0）：reflector compare-first 真改优于建、最小权限不越界；顶层
  PreToolUse backstop 运行时真 deny 一次 `Write`。归 `experiments/` + 手测 runbook。
- [ ] **validate #416 子查补全**（Phase 2/3）：v1 结构查 = frontmatter + name/description +「被引且存在的
  `.py` 语法解析」；**引用文件存在性 / 断 symlink** 待 intent 带显式文件清单再加（按散文路径串硬查会误杀
  正当散文）。frontmatter 是最小 `key: value` 解析（非全 YAML）。
- [ ] **intent_queue durable 格式定稿**（与 [validate-store](research-loom/design/validate-store.md)「intent 队列是否持久」待解同）：
  v1 = repo state 区 per-run `*.jsonl`，read 不删 / land 后 clear（at-least-once）；最终格式 / 粒度待定。
- [ ] **stage_skill MCP 进程绑定接 Phase 7**：Phase 3 只交付确定性处理器（`stage_skill/server.py` 的
  `TOOL_SCHEMA` + `stage()`，schema 强制 + 即时反馈 + 只 append）；stdio JSON-RPC `serve()` 外壳 + 顶层
  `.mcp.json` 注册随打包落地——零依赖禁 `mcp` SDK，wire 形态依 Phase 0 MCP-scope spike 结论。`run_id`/`root`
  由 spawn（Phase 5）经环境注入，现作入参。见 [stage-skill](research-loom/design/stage-skill.md) 待解。
- [ ] **promoter LED watermark + create anchor 接 CAP**（Phase 4）：v1 LED 条目 = `{action, reason, evidence}`、
  无 watermark；create 的 sidecar `anchor` 由调用方入参、缺省 0。CAP（per-turn 计数）建好后供真值。
- [ ] **promoter 逐条幂等 watermark**（与 intent_queue 粒度定稿同）：v1 整 run `clear`，崩溃极窗（land 与
  clear 之间）补处理会重 append 同一 LED 条目（SKILL.md 写幂等、LED 非幂等）。逐 intent watermark 待队列粒度定。
- [ ] **promoter 跨进程单写者锁**（与 sidecar/ledger 并发锁、mng 待解合一）：v1 单进程同步即「串行」，
  两 run 并发同改一 skill 的锁粒度（last-writer）待定。
- [x] **delete 归档 + MNG 退役编排（Phase 6 落）**：`lib/lifecycle.py`（率 + 缓刑 + 容量竞争判定）+
  `hook/on_session_start.py`（惰性现算 → 逐个 `skill_store.archive`）+ `skill_store.restore`（可逆复活）落地。
  设计「只归档不删除」故无 `.archive` 保留期 / GC——archived 永久可 restore，非待 GC。
- [x] **Phase 5 reflector 正文借 Hermes skill-create review-fork prompt**：`agents/reflector.md` 落地——
  compare-first review + authoring 正文仿 Hermes `_SKILL_REVIEW_PROMPT`，去其进程内 fork / 直接写盘假设
  （我方 reflector 只发 intent、碰不到盘），接 compare-first 偏好序 + 运行时注入的单一来源 `format_spec`；
  最小权限工具集（无 Write/Edit/Bash）由 `tests/test_reflector_agent.py` 守。
- [ ] **CAP 孤儿会话计数 GC（policy 仍缺存活信号）**：`on_session_start` 已建（Phase 6），但「哪个
  `session-<id>` 是孤儿」需会话存活信号——朴素扫删会误删并发会话的活计数，故 GC 暂不接进 `on_session_start`。
  `clear_session` 原语已备（Phase 4），等存活信号再落。见 [cap](research-loom/design/cap.md) 待解。
- [x] **CAP 触发裁决 → 真 spawn 接 Phase 5**：`hook/spawn.py` 落地——确定性拼三件套（脱敏窗 + 两层描述索引 +
  注入式 `format_spec`）→ 子会话 spawn（递归 guard + run_id/root 环境注入）→ 接 `promoter.drain`；跨进程闭环由
  fake-reflector system 测覆盖。
- [ ] **spawn 的 host-detach + transcript 上界接 Phase 7**：`run()` 现是同步作业体（spawn→wait→drain）；
  「不堵宿主 `Stop`」的顶层后台启动归 Phase 7 dispatch。触发→读取 race 的 transcript 上界仍 v0 容忍
  （随 spawn 带上界，cap.md 待解）。
- [ ] **公开发布的语言切换（发布期，非现在）.** 现在中文做工作语言；公开时需英文。**不要常驻双分支**
  （dev 中文藏 + public 英文活 → 永久手动同步，违反「一个事实一个权威源」）。两条可选：① 一次性切换——
  发布日做一次中→英全量翻译，之后工作语言换英文（中文留 git 历史）；② 翻译当发布步骤——继续用中文，
  每次发版从 `main` 拉 `release-en` 翻译后 PR、用完即弃，中文为唯一活分支。优先 ①。注意：真正必须英文的是
  README + 面向用户 public docs + 代码标识符；`docs/design/`、`docs/plans/` 是内部设计稿，可缩小翻译面。

- [x] **Wire doc checkers into CI.** Done: `.github/workflows/ci.yml` runs both checkers +
  `--selftest` + `pytest -m "not live"` (tolerates empty collection until product tests land).
  Test strategy & execution order in `docs/plans/roadmap.md`.
