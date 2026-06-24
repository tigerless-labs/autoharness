# [论文] Automating SKILL.md Generation for Computer-Using Agents via Interaction Trajectory Mining

**Yuexing Hao (MIT), Xiaomin Li (Harvard)** — [arXiv:2606.20363](https://arxiv.org/abs/2606.20363) · 2026-06.

Question: hand-written skill files are a bottleneck (must be named, scoped, documented, kept in sync as interfaces change). Can a `SKILL.md` library be **mined from interaction trajectories** in a way that actually improves the downstream policy? **A diagnostic study — the headline answer is "not yet."**

Method — three-stage pipeline:
1. **Segmentation:** cut GUI trajectories at change-points where adjacent-action Euclidean distance exceeds a threshold (tuned on held-out data to maximize boundary F1).
2. **Library construction:** each segment → a length-invariant **bag-of-actions summary** (mean/variance, *order discarded*) → Wasserstein (Bures) agglomerative clustering (k=8–16) → supervised-contrastive MLP refinement.
3. **Skill-aware GRPO:** Qwen3-8B trained with GRPO, scored by an **offline learned reward model** (trained on pairwise preferences, *not* on live task-success labels).

Key results — **readability ≠ transfer**:
- Clusters are readable on the source benchmark (InteraSkill Workflows): 5/8 clusters ≥0.95 purity.
- But GRPO lifts IW skill-step accuracy only 18.5%→20.5%, leaves BrowseComp+ flat (43.5%→43.3%), and **drops** WebArena (55.8%→44.2%).
- A trivial **frequency prior beats** the learned MLP/GRPO policies (34.9% on IW); exact-sequence match is 0%.

Four named failure causes: boundary detector **over-splits** (high recall, low precision); **orderless representation** discards the sequence that makes GUI skills executable (select-before-copy); the **reward model is a proxy** (ranks skill-flow similarity, not cross-domain success); the threshold is **not domain-stable** (IW→WebArena boundary F1 = 0.119).

**Relevance to autoharness:** the most useful *negative* result in the corpus — a direct cautionary tale on autoharness's own premise (mine trajectories → skill files). Three load-bearing warnings: (1) **inspectability is not improvement** — clean, high-purity mined skills can still fail to transfer, so a harness edit must gate on *net task improvement*, never on how readable the artifact looks (reinforces the [operational definition](../../synthesis/offline-validation.md)); (2) **order matters** — any trace→skill representation that throws away sequence loses what makes a skill executable; (3) **offline proxy rewards underperform trivial priors** — a learned scorer not anchored to task success is worse than counting frequencies, hardening the case for [structural / replay-based gating](../../ideas/structural-gate-no-oracle.md) over a trained reward model.
