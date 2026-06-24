# [论文] OpenClaw-Skill: Collective Skill Tree Search for Agentic Large Language Models

**Tianyi Lin, Chuanyu Sun, Jingyi Zhang, Changxu Wei, Huanjin Yao, Shunyu Liu, Xikun Zhang, Liu Liu, Jiaxing Huang** (HK PolyU · NTU · Tsinghua · RMIT · BUAA) — [arXiv:2606.16774](https://arxiv.org/abs/2606.16774) · 2026-06 · 13pp.

Problem: equipping LLM agents with reusable skills (for tool use, multi-step reasoning, dynamic-environment interaction) is the bottleneck in real systems like [OpenClaw](../github/openclaw.md). Construct a structured, diverse, **generalizable tree of skills** automatically.

Method — **Collective Skill Tree Search (CSTS)**, two iterative phases driven by *collective intelligence* (multiple models, not one):
- **CSN-Gen** (node generation): pools collective knowledge from multiple models to explore diverse candidate skills per subtask — broad exploration, not single-model bias.
- **CSN-Assess** (node assessment): multiple models as judges, two scores — (1) **collective quality scoring** aggregates independent evaluations into a robust effectiveness estimate; (2) **collective transferability scoring** explicitly checks whether a skill generalizes *across different models*.
- **Collective Skill Reinforcement Learning (CSRL)**: actively selects *multiple* relevant skills from the tree per problem to broaden solution-space search, so the policy isn't trapped by one skill's homogeneous/suboptimal solution.

Result: trained model OpenClaw-Skill reports strong long-horizon planning, tool use, and generalization on challenging benchmarks (abstract-level; specific numbers in full PDF).

**Relevance to autoharness:** two transplantable ideas. (1) **Collective transferability scoring** is a benchmark-free validation signal — "does this skill help models *other than the one that wrote it*" is a judge-consensus gate that needs no labeled oracle, sitting at point 3 of the [validation-signal spectrum](../../synthesis/benchmark-free-validation.md) and a concrete counter to [self-eval bias](skilllens.md). (2) CSRL's multi-skill selection is an explicit hedge against [exploration collapse](apex.md). **Caveat:** CSTS *grows* a skill tree (add/compose), whereas autoharness's wedge is per-rule *maintenance* under net-improvement gating ("curate, not grow"); borrow its assessment signal, not its growth bias.
