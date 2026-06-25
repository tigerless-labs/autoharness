# [论文] QuartetFuzz: Quality-Assured Fuzz Harness Generation via the Four Principles Framework

**(authors not captured)** — [arXiv:2605.21824](https://arxiv.org/abs/2605.21824) · 2026-05 · code: [OwenSanzas/QuartetFuzz](https://github.com/OwenSanzas/QuartetFuzz).

> Adjacent reference — fuzz-**driver** harness, a different "harness" from this project's agent harness. Kept for the output-quality-validation lesson.

Four-principles correctness (Logic / API-protocol / Security-boundary / Entry-point) in a generate-check-fix loop before fuzzing. 42 reports, 29 fixed/confirmed (3 CVEs), 4.8% FP; P1/P2 checks intercepted 58 harness-induced false crashes.

**Relevance to autoharness:** the most on-point fuzzing analogue — automatic pre-emission quality checks to avoid flooding the recipient with noise, mirroring the gate-before-commit discipline. See [synthesis/](../../synthesis/index.md) for the shared "triage is mandatory" lesson.
