# Defining harness quality without a benchmark

The core 2026-05/06 question: "no benchmark → can't define harness quality." Consensus answer: **bootstrap a validation set from your own past trajectories (especially failures)**. Four routes:

- **RHO — Retrospective Harness Optimization** ([arXiv:2606.05922](https://arxiv.org/abs/2606.05922)) — most direct answer. No ground truth at all: DPP-selected difficulty-diverse coreset of past tasks → re-solve G× in parallel → self-validation + self-consistency → candidate edits picked by the agent's own **pairwise self-preference** (applied only if mean preference positive). SWE-Bench Pro 59→78% in one round, zero external grading.
- **Self-Harness** ([arXiv:2606.09498](https://arxiv.org/abs/2606.09498)) — Weakness Mining (model-specific failures from traces) → minimal harness edits → **regression-test-gated** acceptance. Held-out pass-rate gains across 3 model families.
- **HarnessFix** ([arXiv:2606.06324](https://arxiv.org/abs/2606.06324)) — answers "which harness layer caused the failure": raw traces + harness code → Harness-aware Trace IR → step-level failure attribution → scoped repair operators, gated against regressions.
- **Bayesian-Agent** ([arXiv:2606.08348](https://arxiv.org/abs/2606.08348)) — fixes "treating success/fail counts as reliable belief": each skill/SOP is a hypothesis; maintain a feature-conditioned posterior; map it to auditable actions **patch / split / compress / retire / explore**.
- **MOSS** ([arXiv:2605.22794](https://arxiv.org/abs/2605.22794)) — closest to production. Argues text-layer evolution (skill/prompt/memory) can't reach routing/hooks/state-invariants that live in **code**; does source-level self-rewriting anchored to auto-curated production-failure batches, replay-verified in ephemeral workers, consent-gated in-place swap with health-probe rollback. Evaluated on OpenClaw (0.25→0.61, one cycle, no human).

Also: **APEX** ([arXiv:2605.21240](https://arxiv.org/abs/2605.21240)) warns of **exploration collapse** — as memory grows, behavior concentrates on familiar high-reward routines; worse when there's no benchmark to reveal better options. Keep an explicit exploration budget.

And: **What makes a harness a harness** ([arXiv:2606.10106](https://arxiv.org/abs/2606.10106)) — operational necessary/sufficient definition of "agent harness", with inclusion/exclusion test against framework/SDK/orchestrator/eval-harness. Useful for the design doc's vocabulary.

**Operational definition that emerged:** *new harness must verifiably net-improve (repairs > regressions) on a replay set built from your own history (esp. failures), with each change minimal, auditable, and rollback-able.* = regression-testing discipline applied to harness evolution.
