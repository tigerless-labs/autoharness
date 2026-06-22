# Skill-MAS — evolving a meta-skill for multi-agent systems

**Lin (HKUST-GZ), Yang (Ant Group), Qin (HKUST-GZ, corr.)** — "Skill-MAS: Evolving Meta-Skill for Automatic Multi-Agent Systems" ([arXiv:2606.18837](https://arxiv.org/abs/2606.18837), 2026-06). Code: [linhh29/Skill_MAS](https://github.com/linhh29/Skill_MAS).

Problem: automatic multi-agent systems trade off capability vs. experience retention — inference-time methods use strong frozen LLMs but can't learn from past runs; training-time methods learn but are capped at small models. Skill-MAS is a third path: **decouple experience retention from parametric updates** by treating orchestration capability as an evolvable **Meta-Skill** (NL documentation spanning task decomposition, agent engineering, workflow orchestration).

Optimization loop:
- **Multi-Trajectory Rollout** — K independent trajectories per task turn single outcomes into distributional statistics (uncertainty + difficulty), separating capability from execution noise.
- **Selective Reflection** — prioritize volatile/hard tasks (joint score + elbow truncation), then hierarchical contrastive analysis (within-task → cross-task) to distill strategy-level principles. Best validation-scoring skill picked for test.

Results: 4 benchmarks (DeepResearchBench, HLE-Math, BrowseComp-Plus, VitaBench) × 4 LLMs; beats inference-time and training-time baselines by a large margin (one exception) at a better cost-performance point. Evolved Meta-Skills transfer across unseen tasks and across LLMs.

**Relevance to autoharness:** lifts the skill-as-trainable-state paradigm from the sub-agent to the **meta-agent orchestration** level, with a held-out validation gate — same selection discipline as [SkillOpt](../skill-learning-papers.md). The orchestration layer is itself harness-shaped.
