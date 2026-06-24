# GitHub 与项目 — `[GitHub]` 卡

每个**非**论文官方代码的仓库一张卡。Star 数 ≈ 2026-06-10。论文官方实现从其[论文卡](../papers/index.md)链接，并在下方索引。

## 带记忆 / 自学习的开源 agent

- [NousResearch/Hermes-Agent](nousresearch-hermes-agent.md) — 自动创建 skill；`memory` 工具；按容量驱动的整固。
- [openclaw/openclaw](openclaw.md) — MEMORY.md + Dreaming 整固（按召回效用而非按改进来 gate）。
- [All-Hands-AI/OpenHands](all-hands-openhands.md) — skills 目录 + AGENTS.md；无学习循环（基线）。
- [tinyhumansai/OpenHuman](tinyhumansai-openhuman.md) — Karpathy llm-wiki 的产品化：Markdown 记忆树（SQLite + Obsidian vault），基于文件、无向量。
- [plastic-labs/honcho](plastic-labs-honcho.md) — 辩证式用户建模（Hermes 在用）。
- [microsoft/SkillOpt → SkillOpt-Sleep](microsoft-skillopt-sleep.md) — bootstrap-validation 的工程骨架。

## Skill 生态（内容包 — 热度参考）

- [obra/superpowers](obra-superpowers.md) — ~223k★；强制工作流，无自动学习。
- [affaan-m/ECC](affaan-m-ecc.md) — ~212k★；精选包 + Instincts 自动学习循环。
- [anthropics/skills](anthropics-skills.md) — ~149k★；官方 Agent Skills。
- [mattpocock/skills](mattpocock-skills.md) — ~124k★。
- [hesreallyhim/awesome-claude-code](hesreallyhim-awesome-claude-code.md) — ~46k★；精选清单。
- karpathy-skills — ~173k★（内容包；仅索引，无卡）。

## 同名冲突 — 三个 ~300★、都叫 “AutoHarness”、含义各异的仓库

- [aiming-lab/AutoHarness](aiming-lab-autoharness.md) — ~311★；agent **治理**框架。
- [parikhakshat/autoharness](parikhakshat-autoharness.md) — ~292★；**fuzzing** harness 生成器。
- [kayba-ai/autoharness](kayba-ai-autoharness.md) — ~290★；**依赖 benchmark** 的优化器产品。

## 趋势交叉项目（autoharness × 自我改进）

- [hexo-ai/sia](hexo-ai-sia.md) — 开源自改进 AI。
- [sjhalani7/vaen](sjhalani7-vaen.md) — 可移植的 AI 编码 agent harness。
- [Recursi](recursi.md) — 自改进编码环境（recursi.dev；非仓库）。

## 论文官方实现（在各自论文卡中覆盖）

| 仓库 | ★ | 论文卡 |
|---|---|---|
| [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) | ~5,640 | [SkillOpt](../papers/skillopt.md) |
| [sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill) | ~870 | [EvoSkill](../papers/evoskill.md) |
| [Qwen-Applications/Trace2Skill](https://github.com/Qwen-Applications/Trace2Skill) | ~123 | [Trace2Skill](../papers/trace2skill.md) |
| [DataArcTech/Bayesian-Agent](https://github.com/DataArcTech/Bayesian-Agent) | ~27 | [Bayesian-Agent](../papers/bayesian-agent.md) |
| [wbopan/retro-harness](https://github.com/wbopan/retro-harness) | ~14 | [RHO](../papers/rho.md) |
| [yccm/SkillGen](https://github.com/yccm/SkillGen) | ~10 | [SkillGen](../papers/skillgen.md) |
| [hkgai-official/Moss](https://github.com/hkgai-official/Moss) | ~8 | [MOSS](../papers/moss.md) |
| [OwenSanzas/QuartetFuzz](https://github.com/OwenSanzas/QuartetFuzz) | — | [QuartetFuzz](../papers/quartetfuzz.md) |
| [Cassie07/AgentSkill_Survey](https://github.com/Cassie07/AgentSkill_Survey) | — | [Agent Skill Eval survey](../papers/agent-skill-eval-survey.md) |
| [Huangdingcheng/SkillWiki](https://github.com/Huangdingcheng/SkillWiki) | — | [SkillWiki](../papers/skillwiki.md) |
| [linhh29/Skill_MAS](https://github.com/linhh29/Skill_MAS) | — | [Skill-MAS](../papers/skill-mas.md) |
| [zjunlp/SkillAdaptor](https://github.com/zjunlp/SkillAdaptor) | —（计划中） | [SkillAdaptor](../papers/skilladaptor.md) |
| [Ericbai06/SkillDAG](https://github.com/Ericbai06/SkillDAG) | — | [SkillDAG](../papers/skilldag.md) |
| [plusnli/skill-dynamic-retrieval](https://github.com/plusnli/skill-dynamic-retrieval) | — | [SGDR](../papers/sgdr-web-agents.md) |

**社区移植**（[SkillOpt](../papers/skillopt.md) / [Trace2Skill](../papers/trace2skill.md) 的热度信号）：[joshhu/skillopt-qa](https://github.com/joshhu/skillopt-qa)（~53★，最小复现）· [mitkox/SkillOpt](https://github.com/mitkox/SkillOpt)（~73★，本地模型）· [magnus919/hermes-SkillOpt](https://github.com/magnus919/hermes-SkillOpt)（~11★，Hermes 移植）· [Hert4/trace2skill](https://github.com/Hert4/trace2skill)（harness 无关）。
