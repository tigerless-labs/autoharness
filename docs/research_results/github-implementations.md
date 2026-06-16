# GitHub implementations of the academic work

Academic→OSS conversion is fast (SkillOpt: paper 5/22, ~5.6k★ by 6/10).

**Official paper code:**
| Paper | Repo | ★ (2026-06-10) |
|---|---|---|
| SkillOpt | microsoft/SkillOpt | ~5,640 |
| EvoSkill | sentient-agi/EvoSkill | ~870 |
| Trace2Skill | Qwen-Applications/Trace2Skill | ~123 |
| Bayesian-Agent | DataArcTech/Bayesian-Agent | ~27 |
| RHO | wbopan/retro-harness | ~14 (author = first author Wenbo Pan) |
| SkillGen | yccm/SkillGen | ~10 |
| MOSS | hkgai-official/Moss | ~8 |

**No public implementation:** HarnessFix, the Lou et al. AutoHarness original (DeepMind, no code), Self-Harness.

**Community ports** (heat signal): SkillOpt has the most — joshhu/skillopt-qa (53★ minimal repro), mitkox/SkillOpt (73★ local-model), magnus919/hermes-SkillOpt (port into Hermes). Trace2Skill has 4-5 repros.

**Bootstrap-validation OSS (no benchmark required), confirmed two:**
- wbopan/retro-harness — RHO official; no ground truth, pure self-preference/self-consistency; optimizes CLAUDE.md/auto-memory/scripts (= autoharness's exact target).
- hkgai-official/Moss — production failure-replay; 30-min passive scan + `moss evo flag`; trial-worker replay; 90s health-probe + rollback.

(OpenClaw Dreaming is **not** in this set: its gate is recall utility, not a replay-based net-improvement test — memory management, not harness validation. See oss-memory-self-learning.md.)

**NAME COLLISION — three ~300★ repos called "AutoHarness", all different things:**
1. aiming-lab/AutoHarness (~311★) — agent **governance** framework (Parse→Risk Classify→Permission→Sanitize→Audit). NOT the Lou et al. paper. Has a dubious disclaimer about Claude Code source leaked via npm 2026-03-31 — treat cautiously.
2. parikhakshat/autoharness (~292★) — **fuzzing harness** generation.
3. kayba-ai/autoharness (~290★) — autonomous harness optimizer **product** (requires a benchmark command; Kayba sells managed optimization).

→ This project's name collides head-on. The CLAUDE.md "one-line wedge" TODO must distinguish from governance / fuzzing / benchmark-requiring optimizer in one sentence. Natural differentiator: benchmark-free, production-trajectory-bootstrapped harness evolution (the gap kayba doesn't cover; only 14★ retro-harness occupies it).
