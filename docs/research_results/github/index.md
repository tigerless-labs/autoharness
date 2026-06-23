# GitHub & projects — `[GitHub]` cards

One card per repo that is **not** a paper's official code. Star counts ≈ 2026-06-10. Official paper implementations are linked from their [paper card](../papers/index.md) and indexed below.

## OSS agents with memory / self-learning

- [NousResearch/Hermes-Agent](nousresearch-hermes-agent.md) — auto skill creation; `memory` tool; capacity-driven consolidation.
- [openclaw/openclaw](openclaw.md) — MEMORY.md + Dreaming consolidation (recall-utility gate, not improvement).
- [All-Hands-AI/OpenHands](all-hands-openhands.md) — skills dir + AGENTS.md; no learning loop (the baseline).
- [tinyhumansai/OpenHuman](tinyhumansai-openhuman.md) — Karpathy LLM-wiki productized: Markdown Memory Tree (SQLite + Obsidian vault), file-based, no vectors.
- [plastic-labs/honcho](plastic-labs-honcho.md) — dialectic user modeling (used by Hermes).
- [microsoft/SkillOpt → SkillOpt-Sleep](microsoft-skillopt-sleep.md) — the bootstrap-validation engineering skeleton.

## Skill ecosystem (content packs — heat reference)

- [obra/superpowers](obra-superpowers.md) — ~223k★; mandatory workflows, no auto-learning.
- [affaan-m/ECC](affaan-m-ecc.md) — ~212k★; curated pack + Instincts auto-learning loop.
- [anthropics/skills](anthropics-skills.md) — ~149k★; official Agent Skills.
- [mattpocock/skills](mattpocock-skills.md) — ~124k★.
- [hesreallyhim/awesome-claude-code](hesreallyhim-awesome-claude-code.md) — ~46k★; curated list.
- karpathy-skills — ~173k★ (content pack; index-only, no card).

## Name-collision — three ~300★ repos called "AutoHarness", all different things

- [aiming-lab/AutoHarness](aiming-lab-autoharness.md) — ~311★; agent **governance** framework.
- [parikhakshat/autoharness](parikhakshat-autoharness.md) — ~292★; **fuzzing** harness generator.
- [kayba-ai/autoharness](kayba-ai-autoharness.md) — ~290★; benchmark-**requiring** optimizer product.

## Trending intersection projects (autoharness × self-improvement)

- [hexo-ai/sia](hexo-ai-sia.md) — open-source self-improving AI.
- [sjhalani7/vaen](sjhalani7-vaen.md) — portable AI coding-agent harnesses.
- [Recursi](recursi.md) — self-improving coding environment (recursi.dev; not a repo).

## Official paper implementations (covered in their paper cards)

| Repo | ★ | Paper card |
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
| [zjunlp/SkillAdaptor](https://github.com/zjunlp/SkillAdaptor) | — (planned) | [SkillAdaptor](../papers/skilladaptor.md) |
| [Ericbai06/SkillDAG](https://github.com/Ericbai06/SkillDAG) | — | [SkillDAG](../papers/skilldag.md) |
| [plusnli/skill-dynamic-retrieval](https://github.com/plusnli/skill-dynamic-retrieval) | — | [SGDR](../papers/sgdr-web-agents.md) |

**Community ports** (heat signal for [SkillOpt](../papers/skillopt.md) / [Trace2Skill](../papers/trace2skill.md)): [joshhu/skillopt-qa](https://github.com/joshhu/skillopt-qa) (~53★, minimal repro) · [mitkox/SkillOpt](https://github.com/mitkox/SkillOpt) (~73★, local-model) · [magnus919/hermes-SkillOpt](https://github.com/magnus919/hermes-SkillOpt) (~11★, Hermes port) · [Hert4/trace2skill](https://github.com/Hert4/trace2skill) (harness-agnostic).
