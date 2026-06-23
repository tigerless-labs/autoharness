# [论文] From Raw Experience to Skill Consumption (SkillLens)

**(authors not captured)** — [arXiv:2605.23899](https://arxiv.org/abs/2605.23899) · 2026-05 · no public code.

Full-lifecycle study of model-generated skills. Findings: skills are beneficial on average but show **non-trivial negative transfer**; a strong extractor can be a weak consumer; utility is independent of model scale. Source of the widely-cited **"LLM self-eval ≈ 46.4% accuracy"** warning.

**Relevance to autoharness:** the empirical case for gating — negative transfer is real, so additions must be net-improvement-tested, and self-eval-only signals (the right end of the [validation-signal spectrum](../synthesis/benchmark-free-validation.md)) are noisy enough to need guardrails.
