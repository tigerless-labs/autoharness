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
- [ ] **promoter LED watermark + create anchor 接 CAP**（Phase 4）：v1 LED 条目 = `{action, reason, evidence}`、
  无 watermark；create 的 sidecar `anchor` 由调用方入参、缺省 0。CAP（per-turn 计数）建好后供真值。
- [ ] **promoter 逐条幂等 watermark**（与 intent_queue 粒度定稿同）：v1 整 run `clear`，崩溃极窗（land 与
  clear 之间）补处理会重 append 同一 LED 条目（SKILL.md 写幂等、LED 非幂等）。逐 intent watermark 待队列粒度定。
- [ ] **promoter 跨进程单写者锁**（与 sidecar/ledger 并发锁、mng 待解合一）：v1 单进程同步即「串行」，
  两 run 并发同改一 skill 的锁粒度（last-writer）待定。
- [ ] **delete 归档 = 移进 `.archive`（Phase 2 落）**；最终「交 MNG 归档」的退役编排（保留期 / GC）属 Phase 6 lifecycle。
- [ ] **Phase 5 reflector 正文借 Hermes skill-create review-fork prompt**：`agents/reflector.md` 的 compare-first
  review + authoring 正文以 Hermes 后台 fork 的创建/复盘 prompt 为蓝本（`_spawn_background_review` 的
  `_SKILL_REVIEW_PROMPT` / `build_learn_prompt`，见 [hermes 源卡](research-loom/sources/github/nousresearch-hermes-agent.md)），
  在 Phase 5 补；改写要点：去掉 Hermes 进程内 fork / 直接写盘假设（我方 reflector 只发 intent、碰不到盘），
  接我方 compare-first 偏好序 + 单一来源 `format_spec`。设计已记「仿 `_SKILL_REVIEW_PROMPT`」于
  [reflector-subagent](research-loom/design/reflector-subagent.md)。
- [ ] **CAP 孤儿会话计数 GC 接 Phase 6**：崩溃 session 的 `session-<id>` 计数器残留，走 `on_session_start`
  惰性扫删——该文件在 Phase 6（MNG）建，CAP 出 `clear_session` 原语先备。见 [cap](research-loom/design/cap.md) 待解。
- [ ] **CAP 触发裁决 → 真 spawn 接 Phase 5**：Phase 4 `on_stop`/`on_session_end` 只出「是否触发 + 窗口 N」、
  `capture.materialize` 备好脱敏窗物化；detached 后台 spawn reflector 由 Phase 5 `hook/spawn.py` 接（触发→读取
  race 的 transcript 上界也随 spawn 带，cap.md 待解）。
