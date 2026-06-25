# TODO — tracked follow-ups

> Smaller, uncommitted follow-ups and deferrals. Roadmap-level items belong in the design docs.
> Keep this current in real time: add on discovery, remove or check off on completion.

- [ ] **Measure interrogative-filter precision at scale** (Phase 2 entry). E2 sampled precision
  by hand (~5% → ~50%); needs a labelled measurement across projects under `experiments/`.
- [ ] **Applicability-estimator calibration** (Phase 2 entry). The omission denominator
  (`docs/design/attribute.md`) is unvalidated — calibrate against held-out adherence the user
  confirms before any prose-rule omission verdict ships.
- [ ] **Locate the commit-signature instruction symbol.** E3's conflict case needs its source
  symbol identified (system prompt / settings / output-style) so Phase 0 can target the override.
- [ ] **Resolve the live signature conflict for this repo.** The harness instruction to add
  `Co-Authored-By: Claude` conflicts with the user's repeated correction (×11); decide retire vs
  hookify-override. Until resolved, this repo's own commits reproduce the flaw (see E3).
- [ ] **Decouple E1–E3 phrase lists into config.** The correction/theme phrase sets are inline in
  the experiment scripts; when the detector becomes product code it must move to config
  (`CLAUDE.md` "config holds every knob").
- [ ] **Recreate `DEFINITION.md`.** Removed in commit `bdfd3c3`, never recreated. The dangling link
  from `docs/index.md` is now neutralized to plain text (link checker green), but the authoritative
  project definition still needs writing — the spine 决策 (zero-intrusion / trace-as-candidate /
  must-always-via-hook) is its draft seed (`research-loom/design/spine.md`).
- [ ] **Relocate the `ecosystem-heat` content.** The deleted `synthesis/ecosystem-heat.md` is no
  longer linked — the 8 source cards + `research-loom/index.md` now point at `synthesis/index.md` as a
  stopgap (matching `sources/papers/index.md`; link checker green). Still open: fold the
  ecosystem-heat / positioning / output-quality content into a real synthesis note and relink the cards.
- [ ] **生命周期/去重的触发时机:适配非常驻宿主.** Hermes 的 curator 靠常驻 daemon(空闲 2h / 间隔 7d 自动醒);
  Claude Code 等是临时进程,会话间无常驻、不会空闲自动醒,墙钟周期 sweep 无执行者。需定:失活走惰性判定
  (SessionStart/注入时按时间戳现算)、去重走准入事件驱动;并决定失活刻度用墙钟天还是使用相对(几次会话未被用)。
  见 [`research-loom/ideas/adherence-driven-curate.md`](research-loom/ideas/adherence-driven-curate.md) 的待解。
- [ ] **Wire doc checkers into CI.** `tools/check_doc_links.py` + `tools/check_research_loom.py`
  (and their `--selftest`) should gate PRs once a `.github/workflows` exists. Now unblocked — both
  checkers pass clean (no dangling links).
