# Synthesis — defining harness quality without a benchmark

Cross-source synthesis. Per-paper detail lives in each card; this note holds only what no single source owns.

The core 2026-05/06 question: "no benchmark → can't define harness quality." Consensus answer: **bootstrap a validation set from your own past trajectories (especially failures).**

## The validation-signal spectrum (heaviest external dependency → lightest)

1. **Labeled benchmark** — [kayba](../sources/github/kayba-ai-autoharness.md), [SkillOpt paper](../sources/papers/skillopt.md).
2. **Benchmark-anchored regression gate** — [Self-Harness](../sources/papers/self-harness.md) (held-out pass rates), [HarnessFix](../sources/papers/harnessfix.md) (RegressionBound).
3. **Judge-consensus + test-prompts** — darwin-skill-style.
4. **User-feedback signal** — [SkillOpt-Sleep](../sources/github/microsoft-skillopt-sleep.md) (neg/pos feedback, retry chains as labels).
5. **Failure replay** — [MOSS](../sources/papers/moss.md) (production batch replayed on ephemeral workers).
6. **Pure self-preference** — [RHO](../sources/papers/rho.md) (no ground truth at all).

Rightward = more general but more exposed to self-eval bias (cf. [SkillLens](../sources/papers/skilllens.md)'s ≈46.4%). **Every point gates on *task improvement*.** [OpenClaw Dreaming](../sources/github/openclaw.md) is **off this axis** — its gate is recall utility, not improvement, so it is not a harness-validation signal.

## What transfers to autoharness, what doesn't

- **Borrow:** the loop skeleton (weakness-mine → minimal edit → regression gate); step-level attribution + re-diagnose-verify ([HarnessFix](../sources/papers/harnessfix.md)); intervention-style repair-vs-regression accounting ([SkillGen](../sources/papers/skillgen.md)); posterior-over-skills → action lever ([Bayesian-Agent](../sources/papers/bayesian-agent.md)); production collection channels + consent-gated swap + health-probe rollback ([MOSS](../sources/papers/moss.md)); self-preference selection ([RHO](../sources/papers/rho.md)).
- **Don't borrow:** any failure *definition* anchored to a benchmark oracle (Self-Harness, HarnessFix) — autoharness has no benchmark; coarse layer granularity (HarnessFix's 7 layers vs. the per-rule granularity needed); whole-system source rewriting (MOSS, too heavy).
- **Guard against:** [exploration collapse](../sources/papers/apex.md) (keep an explicit exploration budget); [non-monotonic forgetting](../sources/papers/self-evolving-forget.md) (rollback + regression-gating first-class).

## Operational definition that emerged

> A new harness edit must **verifiably net-improve (repairs > regressions)** on a replay set built from your own history (especially failures), with each change **minimal, auditable, and rollback-able**.

= regression-testing discipline applied to harness evolution. The "agent harness" term itself is pinned down by [What Makes a Harness a Harness](../sources/papers/what-makes-a-harness.md).
