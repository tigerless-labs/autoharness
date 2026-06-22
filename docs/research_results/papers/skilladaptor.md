# [论文] SkillAdaptor: Self-Adapting Skills for LLM Agents from Trajectories

**Yu, Xie, Yao, Wang, Liang, Qi, Deng** — "SkillAdaptor: Self-Adapting Skills for LLM Agents from Trajectories" ([arXiv:2606.01311](https://arxiv.org/abs/2606.01311), 2026-05). Code (planned): [zjunlp/SkillAdaptor](https://github.com/zjunlp/SkillAdaptor).

Problem: training-free skill adaptation that updates from **full trajectories or session-level feedback** localizes failure imprecisely and yields "unstable or overly broad revisions." SkillAdaptor is **step-level** with explicit failure attribution, plugging into "OpenClaw-class agent harnesses." For a failed trajectory it: identifies the first actionable fault step → links responsibility to candidate skills → applies targeted updates under explicit **acceptance checks** → keeps the backbone frozen.

Results: WebShop, PinchBench, Claw-Eval with Kimi-K2.5 / GLM-5 / GPT-5.2 — beats no-skill and skill-adaptation baselines on all three (e.g. +1.8 Claw-Eval, +1.7 WebShop success, +1.5 PinchBench). Argues step-level attribution gives **more stable and auditable** weight-free maintenance.

**Relevance to autoharness:** the failure-attribution granularity question — *which* step/skill/harness layer caused the failure — mirrors [HarnessFix](harnessfix.md). Step-level + acceptance-gated is the precise-edit discipline autoharness needs to avoid broad, regressive rewrites.
