# [论文] SkillWiki: A Living Knowledge Infrastructure for Agent Skills

**Huang, Ding, Liu, … Yu, Sui (11 authors)** — "SkillWiki: A Living Knowledge Infrastructure for Agent Skills" ([arXiv:2606.16523](https://arxiv.org/abs/2606.16523), 2026-06). Demo + code: [Huangdingcheng/SkillWiki](https://github.com/Huangdingcheng/SkillWiki).

Premise: Wikipedia manages knowledge, GitHub manages software, but agent skills "still lack an infrastructure for large-scale production, governance, and evolution."

Mechanism: convert heterogeneous knowledge into reusable skill assets while preserving links back to originating evidence (**provenance-aware grounding**). Covers the full lifecycle — knowledge ingestion → skill production → provenance-aware exploration → governance → execution-driven evolution. Delivered as a demonstration system, not a benchmark study.

Vision: knowledge, skills, and execution experience co-evolve in one shared infrastructure.

**Relevance to autoharness:** the *governance + provenance* angle — every skill/harness edit traceable to its evidence — aligns with autoharness's audit/gate/rollback wedge. Infrastructure peer rather than an optimizer.
