# [论文] Retrospective Harness Optimization (RHO)

**Wenbo Pan et al.** — [arXiv:2606.05922](https://arxiv.org/abs/2606.05922) · 2026-06 · code: [wbopan/retro-harness](https://github.com/wbopan/retro-harness) (~14★, author = first author).

**The most direct benchmark-free answer.** No ground truth at all: a DPP-selected difficulty-diverse coreset of past tasks → re-solve G× in parallel → self-validation + self-consistency → candidate edits picked by the agent's own **pairwise self-preference** (applied only if mean preference positive). SWE-Bench Pro 59→78% in one round, zero external grading.

The official repo optimizes CLAUDE.md / auto-memory / scripts — **autoharness's exact target**, and the only repo occupying the benchmark-free corner ([kayba](../github/kayba-ai-autoharness.md) requires a benchmark command).

**Relevance to autoharness:** the lightest-dependency point on the [validation-signal spectrum](../../synthesis/offline-validation.md) (pure self-preference). Most general but most exposed to self-eval bias (cf. [SkillLens](skilllens.md) 46.4%). Keep an explicit exploration budget against the collapse [APEX](apex.md) warns of.
