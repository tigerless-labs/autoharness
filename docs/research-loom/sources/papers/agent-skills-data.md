# [论文] Agent Skills: A Data-Driven Analysis of Claude Skills

**George Ling, Shanshan Zhong, Richard Huang** — [arXiv:2602.08004](https://arxiv.org/abs/2602.08004) · 2026-02 · cs.SE / cs.SI.

Ecosystem-scale empirical study of **40,285 publicly listed Claude skills** (availability / adoption / risk). Findings: bursty releases tracking attention shifts; supply heavily concentrated in SE workflows while IR + content-creation drive adoption (**supply–demand imbalance**); heavy-tailed length but most fit prompt budgets; **strong ecosystem homogeneity with widespread intent-level redundancy**; non-trivial safety risk from skills enabling state-changing / system-level actions.

**Relevance to autoharness:** independent, large-N evidence that the skill corpus is **redundant at the intent level** — the empirical case for structural **dedup/subsume** at admission (our wedge), not just per-skill quality. Homogeneous descriptions are also exactly what makes recall collapse as N grows (similar descriptions become indistinguishable to the router). The state-changing-action risk reinforces the admission **guardrail**. Pairs with [SkillReducer](skillreducer.md) (description hygiene) and feeds [synthesis/skill-recall-execution](../../synthesis/skill-recall-execution.md).
