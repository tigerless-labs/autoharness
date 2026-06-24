# 论文 — `[论文]` 卡

每篇论文一张卡（arXiv + 有官方代码时附链接）。研究笔记 —— 引用与具体细节是价值所在，`docs/design/` 风格规则不适用。

## A. Agent-harness 综合、自我改进与诊断（核心主线）

- [AutoHarness (Lou et al.)](autoharness-lou.md) — 同名之作；harness 即动作边界，harness 即策略。
- [Self-Harness](self-harness.md) — 弱点挖掘 → 最小编辑 → 回归 gate；最依赖 benchmark。
- [HarnessFix](harnessfix.md) — 在已知失败轨迹内做步级归因（HTIR，7 个 ETCLOVG 层）。
- [RHO](rho.md) — 无 benchmark；在重解的历史任务上做纯自偏好。
- [Bayesian-Agent](bayesian-agent.md) — 对 skill 维护后验 → patch/split/compress/retire/explore。
- [MOSS](moss.md) — 源码级改写；生产失败回放；健康探针回滚。
- [What Makes a Harness a Harness](what-makes-a-harness.md) — 可操作定义 + 纳入/排除判据。
- [SkillHone](skillhone.md) — 持久化决策历史（含被否决选项）的 harness。
- [HASP](hasp.md) — skill 即**可执行**的 Program Function；运行时控制 harness + 策略训练 + 演化；与我们相反的自动写入/权重一角。
- [SKILL.md Mining](skillmd-mining.md) — 诊断性**负结果**：从轨迹挖出的 skill 文件可读却不迁移；学到的组件输给频率先验。可检视 ≠ 改进。

## B. Skill 即可训练状态 & 自演化 skill 方法

- [SkillOpt](skillopt.md) — 可控的文本空间优化器；held-out gate（Microsoft）。
- [SkillGen](skillgen.md) — skill 即干预；因果地权衡修复 vs 回归。
- [SkillLens](skilllens.md) — 完整生命周期；负迁移；自评 ≈46.4%。
- [Trace2Skill](trace2skill.md) — 把并行轨迹蒸馏成 skill 目录（Qwen）。
- [EvoSkill](evoskill.md) — 失败驱动的发现；Pareto 选择。
- [MUSE-Autoskill](muse-autoskill.md) — 完整 skill 生命周期；带单元测试的 skill。
- [SkillEvolver](skillevolver.md) — 部署后用 meta-skill 精炼；静默绕过审计。
- [SkillAdaptor](skilladaptor.md) — 步级归因 + 接受 gate、无权重的更新。
- [Socratic-SWE](socratic-swe.md) — 从轨迹导出的 skill 驱动自演化的 SWE 课程。
- [EmbodiSkill](embodiskill.md) — 修订前先区分 skill 有缺陷 vs 执行失误。
- [Skill-MAS](skill-mas.md) — 编排即可演化的 meta-skill；held-out gate。
- [SkillHarness](skillharness.md) — 面向 computer-use agent 的安全 skill；宏/微观分层、风险守卫激活、证据 gate 的稀疏更新（“策展而非生长”）；同名冲突。
- [OpenClaw-Skill](openclaw-skill.md) — 集体式 Skill Tree Search；多模型裁判打分质量 + **跨模型可迁移性**；CSRL 选多个 skill 以避免坍缩。

## C. 大规模 skill 检索与选择

- [SkillDAG](skilldag.md) — 带类型、冲突感知的 skill 图；推理时查询 + 演化。
- [Graph-of-Skills](graph-of-skills.md) — 推理时受预算约束、依赖感知的检索（离线图 + reverse-aware PPR）。
- [SkillGraph](skillgraph.md) — 带类型的 skill 图，经 RL 与策略协同演化（图 + GRPO）；区别于 SkillDAG。
- [SGDR](sgdr-web-agents.md) — 面向 web agent 的逐步、状态锚定检索。
- [MetaTool](metatool.md) — skill 召回的同行评议代理：工具使用**意识** + **选择**（ICLR 2024）；8 个 LLM 都难以选对。
- [SkillReducer](skillreducer.md) — token 效率优化器；55,315 个 skill 的研究（**26.4% 缺路由描述**）；描述卫生 = 召回杠杆。
- [Agent-Skills-data](agent-skills-data.md) — 40,285 个 Claude skill；**意图级冗余/同质化** + 安全风险；结构化去重的实证依据。

## D. 自演化 agent 与记忆

- [TMEM](tmem.md) — 参数化记忆（在线 LoRA 权重）—— 基于权重的反例。
- [APEX](apex.md) — 探索坍缩 + 策略图。
- [Do Self-Evolving Agents Forget?](self-evolving-forget.md) — 非单调的自演化。
- [SkillOS](skillos.md) — 学习 skill 策展。
- [SAGE](sage.md) — 自演化的 agentic 图记忆引擎。
- [EXG](exg.md) — 带经验图的自演化 agent。

## E. 立论、综述与基础设施

- [Externalization in LLM Agents](externalization-review.md) — 总括性综述；harness = 统一层。
- [Agent Skill Evaluation and Evolution](agent-skill-eval-survey.md) — 四种演化范式；六类 benchmark。
- [SkillWiki](skillwiki.md) — wiki 式基础设施；出处感知的演化。
- [Skill-Harnessing RA](skill-harnessing-ra.md) — 面向 skill 中介 agent 的 10 个模式 + 4 层参考架构；harnessing 与 management 之分；多数不变量都能映射到某个具名模式。

## F. 基础背景

- [Voyager](voyager.md) — 可执行 skill 库（2023）。
- [Reflexion](reflexion.md) — 言语强化学习（2023）。
- [TextGrad](textgrad.md) — 经由文本的自动“微分”（2024）。
- [GEPA](gepa.md) — 反思式 prompt 演化可胜过 RL（2025）。

## G. 相邻领域：fuzz-driver / fuzzing-harness 生成（仅参考）

另一种“harness”（fuzz driver）；保留是为了输出质量验证这一教训 —— 见 [synthesis/](../../synthesis/index.md)。

- [QuartetFuzz](quartetfuzz.md) · [Agentic Fuzzing](agentic-fuzzing.md) · [MASFuzzer](masfuzzer.md) · [Multi-Agent Java Harness](java-fuzz-harness.md) · [STITCH](stitch.md) · [HarnessAgent](harnessagent.md) · [FalseCrashReducer](falsecrashreducer.md) · [Scheduzz](scheduzz.md) · [Reliable LLM Fuzz Testing (vision)](reliable-fuzz-vision.md) · [SEC-bench Pro](sec-bench-pro.md)
