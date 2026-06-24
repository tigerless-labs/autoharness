# [论文] Agent Skill Evaluation and Evolution: Frameworks and Benchmarks

**Ding, Zhou, Jin, Tong, Zhou, Metaxas** — "Agent Skill Evaluation and Evolution: Frameworks and Benchmarks" ([arXiv:2606.11435](https://arxiv.org/abs/2606.11435), 2026-06). Code/list: [Cassie07/AgentSkill_Survey](https://github.com/Cassie07/AgentSkill_Survey).

Survey consolidating the shift from "isolated skill creation to automated, evaluation-driven skill evolution."

Two taxonomies:
- **Four evolution paradigms** — execution feedback, trajectory distillation, compression, reinforcement learning.
- **Six skill-centric benchmark categories** — with the paper flagging structural gaps in coverage, trade-offs, and metric richness.

Open direction: skill ecosystems that are generalizable, efficient, and *verifiably safe*.

**Relevance to autoharness:** the evaluation half is the live question for any harness optimizer — how to measure skill/harness utility without overfitting a benchmark. Pairs with [synthesis/offline-validation.md](../../synthesis/offline-validation.md). A companion reading list for cross-checking the cluster.
