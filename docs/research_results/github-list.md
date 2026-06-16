# GitHub list

Repos referenced in the 2026-06-10 research session. ★ counts = approximate, 2026-06-10.

## Official paper implementations

- [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) — ~5,640★. SkillOpt + SkillOpt-Sleep (bootstrap-validation `/sleep` plugins for Claude Code/Codex/Copilot).
- [sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill) — ~870★.
- [Qwen-Applications/Trace2Skill](https://github.com/Qwen-Applications/Trace2Skill) — ~123★.
- [DataArcTech/Bayesian-Agent](https://github.com/DataArcTech/Bayesian-Agent) — ~27★.
- [wbopan/retro-harness](https://github.com/wbopan/retro-harness) — ~14★. RHO official; benchmark-free.
- [yccm/SkillGen](https://github.com/yccm/SkillGen) — ~10★.
- [hkgai-official/Moss](https://github.com/hkgai-official/Moss) — ~8★. MOSS source-level self-rewriting.
- [OwenSanzas/QuartetFuzz](https://github.com/OwenSanzas/QuartetFuzz) — fuzz-harness quality framework + dataset.

## Community ports / re-implementations

- [joshhu/skillopt-qa](https://github.com/joshhu/skillopt-qa) — ~53★. Minimal faithful SkillOpt repro.
- [mitkox/SkillOpt](https://github.com/mitkox/SkillOpt) — ~73★. Local-model SkillOpt.
- [magnus919/hermes-SkillOpt](https://github.com/magnus919/hermes-SkillOpt) — ~11★. SkillOpt ported into Hermes.
- [Hert4/trace2skill](https://github.com/Hert4/trace2skill) — harness-agnostic Trace2Skill.

## Open-source agents with memory / self-learning

- [NousResearch/Hermes-Agent](https://github.com/NousResearch/Hermes-Agent) — auto skill creation, `memory` tool (add/replace/remove), capacity-driven consolidation, nudges (interval 10).
- [openclaw/openclaw](https://github.com/openclaw/openclaw) — MEMORY.md + Dreaming consolidation gated on score/recall-frequency/query-diversity.
- [All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) — context compression, skills dir, AGENTS.md repo memory.
- [plastic-labs/honcho](https://github.com/plastic-labs/honcho) — dialectic user modeling (used by Hermes).

## Skill ecosystem (content packs — heat reference)

- [obra/superpowers](https://github.com/obra/superpowers) — ~223k★. Methodology + mandatory workflows; no auto-learning loop.
- [affaan-m/ECC](https://github.com/affaan-m/ECC) — ~212k★. Curated pack + Instincts (Continuous Learning v2) auto-learning loop.
- [anthropics/skills](https://github.com/anthropics/skills) — ~149k★. Official Agent Skills.
- [mattpocock/skills](https://github.com/mattpocock/skills) — ~124k★.
- [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) — ~46k★. Curated list.

## Name-collision warning — three different "AutoHarness" repos

- [aiming-lab/AutoHarness](https://github.com/aiming-lab/AutoHarness) — ~311★. Agent **governance** framework. NOT the Lou et al. paper.
- [parikhakshat/autoharness](https://github.com/parikhakshat/autoharness) — ~292★. **Fuzzing** harness generator.
- [kayba-ai/autoharness](https://github.com/kayba-ai/autoharness) — ~290★. Harness optimizer **product** (requires a benchmark command).

## Trending intersection projects (autoharness × self-improvement, from last30days)

- [hexo-ai/sia](https://github.com/hexo-ai/sia) — SIA: open-source self-improving AI.
- [sjhalani7/vaen](https://github.com/sjhalani7/vaen) — package/import portable AI coding-agent harnesses.
- [Recursi](https://recursi.dev/) — self-improving LLM-connected coding environment (Show HN).
- henrypan.com blog — ["What 1k Harness Experiments Taught Me About Self-Improving Agents"](https://www.henrypan.com/blog/2026-05-25-self-improvement-harness/) (not a repo, but the closest empirical write-up).
