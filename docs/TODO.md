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
- [x] **实测 MNG 的调用捕获**（S5）。Skill 走 `Skill` 工具触发 `PreToolUse(Skill)`，transcript 另记
  命名空间 `attributionSkill`（`plugin:skill`）—— 分子有真符号 hook。见
  [`experiments/E6_platform_contracts`](../experiments/E6_platform_contracts/results.md)。
- [x] **实测 plugin-shipped agent 是否支持 `hooks` / `mcpServers` frontmatter**（S1）。**否**（安全，2.1.63+
  忽略）。决策：reflector backstop + stage_skill 退到 plugin 顶层 `hooks.json` / `.mcp.json`。见
  [`experiments/E6_platform_contracts`](../experiments/E6_platform_contracts/results.md)。
- [ ] **建 plugin 官方结构源卡**（`sources/`）：`plugin.json` / `hooks/hooks.json`（`${CLAUDE_PLUGIN_ROOT}` + `{"hooks":{...}}` 包裹）/ `agents/` / `.mcp.json` / marketplace —— `architecture.md` 的 provenance 现挂"待建"。
- [ ] **吸收 Phase 0 决策进设计文档**（建 Phase 3/5/6 时，决策现住 E5/E6 证据卡）：mng 率分母锁
  per-turn/per-Stop、分子取命名空间 skill id；reflector backstop=plugin 顶层 `hooks.json` 按 `agent_type`
  匹配；stage_skill 走 plugin `.mcp.json`；cap 只数主 `Stop`（reflector 完成是 `SubagentStop`）。见
  [`docs/plans/phase0-platform-spikes.md`](plans/phase0-platform-spikes.md)。
- [ ] **Phase 5 行为型 live**（非 Phase 0）：reflector compare-first 真改优于建、最小权限不越界；顶层
  PreToolUse backstop 运行时真 deny 一次 `Write`。归 `experiments/` + 手测 runbook。
- [x] **Wire doc checkers into CI.** Done: `.github/workflows/ci.yml` runs both checkers +
  `--selftest` + `pytest -m "not live"` (tolerates empty collection until product tests land).
  Test strategy & execution order in `docs/plans/roadmap.md`.
