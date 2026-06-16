# Paper list

All papers referenced in the 2026-06-10 research session, grouped by theme. Dates = arXiv submission.

## Agent harness synthesis & self-improvement (the core line)

- [AutoHarness: improving LLM agents by automatically synthesizing a code harness](https://arxiv.org/abs/2603.03329) — Lou, Lázaro-Gredilla, Dedieu, Wendelken, Lehrach, Murphy. 2026-02. **The namesake.** Harness as action boundary; harness-as-policy.
- [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498) — 2026-06. Weakness mining → minimal edits → regression-gated.
- [From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws (HarnessFix)](https://arxiv.org/abs/2606.06324) — 2026-06. Trace IR + failure attribution to harness layers.
- [Retrospective Harness Optimization (RHO)](https://arxiv.org/abs/2606.05922) — 2026-06. Benchmark-free; self-preference over re-solved past trajectories.
- [Bayesian-Agent: Posterior-Guided Skill Evolution for LLM Agent Harnesses](https://arxiv.org/abs/2606.08348) — 2026-06. Posterior over skills; patch/split/compress/retire/explore.
- [MOSS: Self-Evolution through Source-Level Rewriting in Autonomous Agent Systems](https://arxiv.org/abs/2605.22794) — 2026-05. Source-level rewriting, production failure-replay, rollback-gated.
- [What makes a harness a harness: necessary and sufficient conditions for an agent harness](https://arxiv.org/abs/2606.10106) — 2026-06. Operational definition; inclusion/exclusion test.

## Skill-as-trainable-state cluster

- [SkillOpt: Executive Strategy for Self-Evolving Agent Skills](https://arxiv.org/abs/2605.23904) — Microsoft, 2026-05. Text-space optimizer; held-out gate.
- [SkillGen: Verified Inference-Time Agent Skill Synthesis](https://arxiv.org/abs/2605.10999) — 2026-05. Skills as interventions; causal repair-vs-regression.
- [From Raw Experience to Skill Consumption (SkillLens)](https://arxiv.org/abs/2605.23899) — 2026-05. Full lifecycle; negative transfer; LLM self-eval ≈46.4%.
- [Trace2Skill: Distill Trajectory-Local Lessons into Transferable Agent Skills](https://arxiv.org/abs/2603.25158) — Qwen, 2026-03.
- [EvoSkill: Automated Skill Discovery for Multi-Agent Systems](https://arxiv.org/abs/2603.02766) — 2026-03. Failure-analysis-driven; Pareto selection.
- [MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation](https://arxiv.org/abs/2605.27366) — 2026-05. Skill lifecycle management.

## Self-evolving agents & memory

- [Scaling Self-Evolving Agents via Parametric Memory (TMEM)](https://arxiv.org/abs/2606.04536) — 2026-06. Distilled supervision into fast LoRA weights online.
- [APEX: Autonomous Policy Exploration for Self-Evolving LLM Agents](https://arxiv.org/abs/2605.21240) — 2026-05. Exploration collapse + strategy map.
- [Do Self-Evolving Agents Forget? Capability Degradation and Preservation](https://arxiv.org/abs/2605.09315) — 2026-05. Non-monotonic self-evolution.
- [SkillOS: Learning Skill Curation for Self-Evolving Agents](https://arxiv.org/abs/2605.06614) — 2026-05.
- [SAGE: A Self-Evolving Agentic Graph-Memory Engine](https://arxiv.org/abs/2605.12061) — 2026-05.
- [EXG: Self-Evolving Agents with Experience Graphs](https://arxiv.org/abs/2605.17721) — 2026-05.

## Foundational context (from the Zhihu symbolic-learning essay)

- [Voyager: An Open-Ended Embodied Agent with LLMs](https://arxiv.org/abs/2305.16291) — 2023. Executable skill library.
- [Reflexion: Language Agents with Verbal Reinforcement Learning](https://arxiv.org/abs/2303.11366) — 2023.
- [TextGrad: Automatic "Differentiation" via Text](https://arxiv.org/abs/2406.07496) — 2024.
- [GEPA: Reflective Prompt Evolution Can Outperform RL](https://arxiv.org/abs/2507.19457) — 2025.
- Zhihu essay (framing, login-walled): [符号学习在 Agent 时代的文艺复兴?](https://zhuanlan.zhihu.com/p/2044779283978139242)
- Blog: Jiayi Weng, "Learning Beyond Gradients" (Heuristic Learning) — referenced, no stable URL captured.

## Adjacent: fuzz-driver / fuzzing-harness generation (reference only)

- [QuartetFuzz: Quality-Assured Fuzz Harness Generation via the Four Principles Framework](https://arxiv.org/abs/2605.21824) — 2026-05.
- [Agentic Fuzzing: Opportunities and Challenges](https://arxiv.org/abs/2605.10074) — 2026-05.
- [MASFuzzer: Fuzz Driver Generation and Adaptive Scheduling](https://arxiv.org/abs/2604.17977) — 2026-04.
- [Coverage-Guided Multi-Agent Harness Generation for Java Library Fuzzing](https://arxiv.org/abs/2603.08616) — 2026-03.
- [Automatic, Expressive, and Scalable Fuzzing with Stitching (STITCH)](https://arxiv.org/abs/2602.18689) — 2026-02.
- [HarnessAgent: Scaling Automatic Fuzzing Harness Construction](https://arxiv.org/abs/2512.03420) — 2025-12.
- [HarnessLLM: Automatic Testing Harness Generation via RL](https://arxiv.org/abs/2511.01104) — 2025-11.
- [FalseCrashReducer: Mitigating False Positive Crashes in OSS-Fuzz-Gen Using Agentic AI](https://arxiv.org/abs/2510.02185) — 2025-10.
- [Scheduzz: Constraint-based Fuzz Driver Generation with Dual Scheduling](https://arxiv.org/abs/2507.18289) — 2025-07.
- [Towards Reliable LLM-Driven Fuzz Testing: Vision and Road Ahead](https://arxiv.org/abs/2503.00795) — 2025-03.
- [SEC-bench Pro: Can Language Models Solve Long-Horizon Software Security Tasks?](https://arxiv.org/abs/2605.26548) — 2026-05.
