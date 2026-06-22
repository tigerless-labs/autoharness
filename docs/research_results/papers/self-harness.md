# [论文] Self-Harness: Harnesses That Improve Themselves

**(authors not captured)** — [arXiv:2606.09498](https://arxiv.org/abs/2606.09498) · 2026-06 · no public code.

Loop: **Weakness Mining** (model-specific failures from traces) → minimal harness edits → **regression-test-gated** acceptance. Held-out pass-rate gains across 3 model families (MiniMax M2.5 / Qwen3.5-35B-A3B / GLM-5).

**Most benchmark-bound of the bootstrap cluster — anchored at both ends:** instantiated on **Terminal-Bench-2.0** from a minimal initial harness; failure traces are produced on that benchmark; the Proposal-Validation gate accepts edits only via **held-out pass rates = benchmark ground-truth task success** (not self-eval like HarnessFix's flaw-rate or MOSS's batch-replay).

**Relevance to autoharness:** only the *loop skeleton* (weakness-mine → minimal edit → regression gate) transfers; its failure-sourcing and gate do **not** — they need a benchmark autoharness doesn't have. Compare [rho.md](rho.md) (benchmark-free) at the opposite end of the [validation-signal spectrum](../synthesis/benchmark-free-validation.md).
