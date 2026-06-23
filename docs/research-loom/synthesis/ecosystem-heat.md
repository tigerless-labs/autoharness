# Synthesis — ecosystem heat, virality, and positioning

Cross-source synthesis: how the category gets adopted, and where autoharness sits. Per-repo detail lives in the [github/](../github/index.md) cards.

## The star gap is 2–4 orders of magnitude

Content packs dwarf optimizers:
- **Content:** [superpowers](../github/obra-superpowers.md) ~223k★, [ECC](../github/affaan-m-ecc.md) ~212k★, karpathy-skills ~173k★, [anthropics/skills](../github/anthropics-skills.md) ~149k★, [mattpocock/skills](../github/mattpocock-skills.md) ~124k★.
- **Optimizer/bootstrap:** [SkillOpt](../papers/skillopt.md) ~5.6k★, [EvoSkill](../papers/evoskill.md) ~870★, [kayba](../github/kayba-ai-autoharness.md) ~290★, [retro-harness/RHO](../papers/rho.md) ~14★, [MOSS](../papers/moss.md) ~8★.

**Three structural reasons:** (1) content = copy-paste, zero-config, instant value, audience = every user; infrastructure needs API budget, trust to edit your config, repeat cycles. Stars measure distribution efficiency, not which direction is right (cf. prompt-collections ≫ DSPy in 2023). (2) Time lag — bootstrap papers are 2–6 weeks old (RHO 6 days). (3) Value-realization delay — a skill helps on first use; an optimizer needs accumulated trajectories + several cycles.

## The virality playbook (≈ how superpowers went viral)

Small credibility × **launch-day timing** (shipped the morning Anthropic released the plugin system) × **official-marketplace shelf** × instant felt value. Author fame was the lowest-weight factor (no viral HN post). Stars accrued via blogs/reviews/word-of-mouth. The category wins when packaged as "install-and-it-works content pack + an optional learning loop hidden inside" — [ECC](../github/affaan-m-ecc.md)'s move — not as a research framework.

## Name collision — three ~300★ "AutoHarness" repos

This project's name collides head-on; the wedge must distinguish in one sentence:
- [aiming-lab/AutoHarness](../github/aiming-lab-autoharness.md) — agent **governance**.
- [parikhakshat/autoharness](../github/parikhakshat-autoharness.md) — **fuzzing** harness.
- [kayba-ai/autoharness](../github/kayba-ai-autoharness.md) — benchmark-**requiring** optimizer product.

Plus the fuzzing-paper line (e.g. [QuartetFuzz](../papers/quartetfuzz.md), [FalseCrashReducer](../papers/falsecrashreducer.md)) — a different "harness" that converged on the same lesson: **automatic triage/verification before emission is mandatory; generating candidates is cheap, not flooding the recipient is the hard, valuable part.** Reinforced by ecosystem anxiety (HN "flood of AI garbage", the Miasma worm targeting AI coding agents) → outputs must be gated/verified.

## Positioning takeaway

The contested, low-competition gap is **benchmark-free, trajectory-bootstrapped harness evolution with audit/gate/rollback** — distinct from governance frameworks, fuzz-harness generation, and benchmark-requiring optimizers. Adoption must sit on artifacts users already have (read/write CLAUDE.md & skills dirs, install as plugin/hook, produce a reviewable diff on night one). [ECC](../github/affaan-m-ecc.md) (distribution) + [SkillOpt-Sleep](../github/microsoft-skillopt-sleep.md) (engineering skeleton) + [RHO](../papers/rho.md) (validation method) each own a corner; nobody has all three.
