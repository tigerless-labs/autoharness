# SkillDAG — self-evolving typed skill graphs for selection at scale

**Bai, Wan, Zhou, Yu, Zhao, You, Tsang** — "SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale" ([arXiv:2606.03056](https://arxiv.org/abs/2606.03056), 2026-06, 19pp). Code: [Ericbai06/SkillDAG](https://github.com/Ericbai06/SkillDAG).

Problem: with large skill libraries, picking the right subset is a **structural** problem, not similarity matching — skills "depend on, conflict with, specialize, or duplicate one another," structure hidden from both full enumeration and embedding similarity. SkillDAG encodes inter-skill relations as a **typed directed graph** the agent queries at inference time as a structural retrieval interface; it is "queried and evolved during execution," not fixed in a pipeline. Each search returns vector matches + typed-edge neighbors + **conflict signals**; a **propose-then-commit protocol** lets the agent add execution-backed edges, so structure accumulates across episodes.

Results: ALFWorld + SkillsBench with MiniMax-M2.7 — 67.1% success / 27.3% reward, +12.8 / +8.6 over the strongest Graph-of-Skills baseline; transfers to gpt-5.2-codex; intrinsic Ret@K 65.5 → 78.2. Gains hold as the pool scales 10× (fixed pipelines degrade) via "set-monotone online edits."

**Relevance to autoharness:** the **conflict-aware, self-evolving** structure is what a maturing harness needs once skills/rules multiply — explicit conflict edges are a guardrail against contradictory harness rules. Selection-layer peer to the editing-layer optimizers.
