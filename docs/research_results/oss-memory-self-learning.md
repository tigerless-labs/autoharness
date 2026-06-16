# Open-source memory / self-learning mechanisms

What's actually shipped in open-source agents for automatic memory/skill update.

**OpenClaw** (docs.openclaw.ai) — most complete:
- Memory is plain Markdown on disk (no hidden state): `MEMORY.md` (long-term, curated) + `memory/YYYY-MM-DD.md` (daily).
- **Memory flush**: a silent turn before compaction reminds the agent to save important context. On by default.
- **Dreaming**: background cron consolidation; promotes short-term signals to `MEMORY.md` only past a **score + recall-frequency + query-diversity** gate; summaries to `DREAMS.md`, rollback-able. → memory quality defined by *actual recall frequency and diversity*, not write-time judgment.
  - **Not symbolic learning — memory management.** Dreaming curates context facts; it does not edit a capability artifact (skill/policy/code) or optimize task-solving ability. Its gate is *recall utility* (will this be retrieved again), not *net task improvement* (repairs > regressions on a replay set) — no replay, no improvement test, no backward pass. It rhymes with the symbolic-learning line only in shape (`experience → reflect/edit → on-disk Markdown`, gate-before-commit) and in sharing the same on-disk symbol layer, not in mechanism or goal.

**Hermes** (NousResearch) — autonomous skill creation after complex tasks; **skills self-improve in use**; periodic memory nudges; FTS5 session search + LLM summarization; Honcho user modeling. Also feeds back to model level: batch trajectory generation + trajectory compression to train next-gen tool-calling models.

**OpenHands** — thinnest: auto context compression, skills dir, `AGENTS.md` repo memory; no documented auto-update or experience-learning loop.

**microsoft/SkillOpt → SkillOpt-Sleep** (released 2026-06-08, `skillopt_sleep/` package, decoupled from paper code) — **the bootstrap-validation implementation**:
- Pipeline: harvest own session transcripts → mine TaskRecords (heuristic miner reads user neg/pos feedback + retry chains as labels; optional LLM miner) → **train/val/test split of mined tasks** → replay offline → consolidate with vendored strict-improvement gate → stage for user adoption.
- Code is explicit: "train drives reflect; val gates updates; test held out entirely; never silently use test as val."
- Scoring with no human labels: rule judges (regex/section_present/contains/max_chars/tool_called) → all pass = hard 1.0, fraction = soft; rubric judge for reference-free tasks.
- Ships as Claude Code / Codex / Copilot plugins (`/sleep`). gbrain-evals: deficient skill 0.00→1.00 held-out, gate blocks regressions.

**Timeline note:** SkillOpt-Sleep landed 4 days after RHO (the bootstrap paper, 2026-06-04), all 30 sleep commits squashed on 2026-06-08 ("overnight build"). But no citation link — "trajectory as validation set" converged at multiple points (OpenClaw Dreaming predates both), not a clear lineage.

**Validation-signal spectrum** (heaviest external dependency → lightest): labeled benchmark (kayba / SkillOpt paper) → judge-consensus + test-prompts (darwin-skill) → user-feedback signal (SkillOpt-Sleep) → failure replay (MOSS) → pure self-preference (RHO). Rightward = more general but more exposed to self-eval bias (cf. SkillLens 46.4%). Every point on this spectrum gates on *task improvement*. OpenClaw Dreaming is **off this axis** — its gate is recall utility, not improvement, so it is not a harness-validation signal.
