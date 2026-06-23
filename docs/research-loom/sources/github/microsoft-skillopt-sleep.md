# [GitHub] microsoft/SkillOpt — SkillOpt-Sleep

[github.com/microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) (~5,640★) · `skillopt_sleep/` package, released 2026-06-08, decoupled from the paper code · ships as Claude Code / Codex / Copilot `/sleep` plugins. Implementation of the [SkillOpt paper](../papers/skillopt.md).

**The bootstrap-validation implementation** — the engineering skeleton closest to autoharness:
- Pipeline: harvest own session transcripts → mine TaskRecords (heuristic miner reads user neg/pos feedback + retry chains as labels; optional LLM miner) → **train/val/test split** of mined tasks → replay offline → consolidate with a vendored strict-improvement gate → stage for user adoption. Code is explicit: "train drives reflect; val gates updates; test held out entirely; never silently use test as val."
- **Replay (ClaudeCliBackend):** each task replay is ONE headless `claude -p` subprocess in a fresh `mkdtemp` cwd — no hooks/LSP/plugins, all skills disabled, no tools, dynamic sections stripped. **The candidate skill/memory under test is injected as PROMPT TEXT (`## Skill` / `## Memory`), not as a real installed skill** — so it measures "this text in a prompt", not "this rule as a retrieved/hook-triggered skill".
- Scoring with no human labels: rule judges (regex/section_present/contains/max_chars/tool_called) → all-pass = 1.0, fraction = soft; rubric judge for reference-free tasks. Responses cached on `skill_hash(prompt)` so held-out re-scoring is free.

**Relevance to autoharness:** the reference engineering skeleton — but note the **tension**: clean-sandbox text-injection testing vs. autoharness's target of symbols that take effect *in place* in the live harness (rules actually loaded, hooks actually firing), closer to [MOSS](../papers/moss.md)'s real-failure replay. Landed 4 days after [RHO](../papers/rho.md) with no citation link — convergence, not lineage.
