# [论文] MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems

**(HKGAI)** — [arXiv:2605.22794](https://arxiv.org/abs/2605.22794) · 2026-05 · code: [hkgai-official/Moss](https://github.com/hkgai-official/Moss) (~8★).

Closest to production. Argues text-layer evolution (skill/prompt/memory) can't reach the routing/hooks/state-invariants that live in **code**; does source-level self-rewriting anchored to auto-curated production-failure batches, replay-verified in ephemeral workers, consent-gated in-place swap with health-probe rollback. Evaluated on OpenClaw (0.25→0.61, one cycle, no human).

**Failure sourcing is NOT benchmark-based** (contrast [HarnessFix](harnessfix.md)): errors come from production sessions via two channels — a 30-min cron scanning new session content for *under-performing turns / "weak chunks"*, plus a manual `moss evo flag`. No oracle/threshold defined — "weak" is an unspecified LLM-ish quality judgment, so labeling is exposed to self-eval bias. The **validation set is the failure batch itself** (replayed on ephemeral trial workers); the only grader in the paper *measures* the 0.25→0.61 result, it doesn't label failures.

**Relevance to autoharness:** borrow the collection channels + consent-gated swap + 90s health-probe rollback. Do **not** borrow the whole-system source-rewrite body — too heavy and OpenClaw-bound; autoharness's target is the symbol layer, not source code.
