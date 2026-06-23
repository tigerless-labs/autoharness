# [论文] SkillGraph: Skill-Augmented Reinforcement Learning for Agents via Evolving Skill Graphs

**Xiaoyuan Li, Moxin Li, Keqin Bao, Yubo Ma, Wenjie Wang, Dayiheng Liu, Fuli Feng (USTC / Alibaba / NUS)** — [arXiv:2605.12039](https://arxiv.org/abs/2605.12039), 2026-05-12. ⚠️ distinct from SkillDAG and SkillOps (name collision).

Skills as nodes in a directed graph with typed edges **prerequisite / enhancement / co-occurrence**; a task retrieves an **ordered skill subgraph** (not single skills). Three stages: graph construction (distill skills + typed relations from traces), graph-aware retrieval (seed → expand along edges → topological order → dependency-ordered sequence), graph evolution (node: insert/merge/split/deprecate; edge: reinforce/discover/prune; progressive unlocking). The graph **co-evolves with the agent policy via RL (GRPO)** — closed loop: richer trajectories → better graph → better retrieval → stronger policy. ALFWorld / WebShop / 7 search-augmented QA; SOTA vs memory-augmented RL, large gains on compositional tasks. Most related: SkillRL (elevates a flat skill bank into a typed dependency graph).

**Relevance to autoharness:** hybrid — its **graph lifecycle ops (merge / split / deprecate / prune)** are borrowable management vocabulary; the **RL policy co-evolution (GRPO) is evolution we do not take**. No conflict edge.
