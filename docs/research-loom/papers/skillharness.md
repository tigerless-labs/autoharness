# [论文] SkillHarness: Harnessing Safe Skills for Computer-Use Agents

**Yurun Chen, Biao Yi, Keting Yin, Shengyu Zhang** — [arXiv:2606.20636](https://arxiv.org/abs/2606.20636) · 2026-06-02.

The literal name collision (and the closer one). Targets **computer-use agents (CUAs)**: prior skill learning assumes static/safe environments, so it inherits risky behavior from raw trajectories and breaks under pop-ups / DOM drift.

**Method.** Skill library decoupled into **macro skills** (high-level intent + success patterns + failure lessons + **risk guards** + links) and **micro skills** (parameterized code grounded in current state). The **skill boundary** is induced from three signals — successful trajectories, failure cases, identified risks — so a skill carries *the conditions under which its pattern stays reliable*, not just the executable pattern. Acquisition is **task-free exploration**: a goal proposer fills capability-cluster gaps, an evolution policy does **sparse, evidence-gated** updates. **Safety = risk guards**: policy-derived state constraints that must hold before a micro skill activates; planner suppresses micro skills on state drift and falls back to LLM planning; an **adaptive bypass disables template replay after repeated failures**.

**Numbers.** Unsafe rate of learned skills −57.1%; utilization safety +31.9% avg; SR +19% avg. USR 2.2% vs SkillWeaver 43.6% vs ASI 75.0%. WASP: SR 85.0 / ASR 2.5 (default SR 56.4). **Ablation: removing the skill boundary causes the largest ASR jump (+9.6); removing micro skills changes nothing** — the boundary, not the code, carries the safety. Benchmarks: ST-WebAgentBench, WASP, OS-Harm, OpenApps; GPT-5.4 family + Qwen3.6 / OpenCUA / MAI-UI.

**Referenced directions (Related Work).**
- **A. Skill learning** — [Voyager](voyager.md); ASI, SkillWeaver, Polyskill (code/trajectory skills for CUAs); SkillRL (Xia 2026), Wang 2025a (RL self-improving library). Skill-safety: "Agent Skills in the Wild" (Liu 2026), "When skills lie" / hidden-comment injection (Wang 2026).
- **B. Harness engineering** — Harness-Engineering survey (Lopopolo 2026); prompt eng. (Sahoo 2024); context eng. — Agentic Context Engineering (Zhang 2025), HarmonyGuard (Chen 2025); Agent Workflow Memory (Wang 2024). Intro also: Cascade, CUA-Skill, Mirage-1; human-skill theory (Dreyfus & Dreyfus, Fitts & Posner).

**Relevance to autoharness.** Strong corroboration on our spine, opposite on auto-write:
- "**Stable, curated accumulation rather than maximal growth**" + sparse evidence-gated updates = direct external echo of our **maintain-not-grow** (invariant 2) and **every-change-passes-a-gate** (invariant 7).
- **Risk guards = activation only when state constraints hold** = the executable form of our **applicability gate** (invariant 6 — without applicability it's a candidate, not a verdict) and fail-safe planning (invariant 9).
- **Skill boundary from success+failure+risk; ablating it hurts most** = evidence that the *boundary/condition* is the load-bearing artifact, not the instruction text — matches "objective signal is the spine" (invariant 3).
- **Adaptive bypass after repeated failures** ≈ our exploration budget / anti-collapse (invariant 8).
- **Contrast:** it **auto-learns/auto-writes** skills from task-free exploration (heavily gated) — opposite to our **never-auto-write / human-adoption-as-grounding** (invariant 1); and its domain is GUI/OS state, not our text-harness layer.
