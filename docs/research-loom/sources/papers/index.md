# Papers — `[论文]` cards

One card per paper (arXiv + official code link when it exists). Research notes — citations and specifics are the value; `docs/design/` style rules do not apply.

## A. Agent-harness synthesis, self-improvement & diagnosis (the core line)

- [AutoHarness (Lou et al.)](autoharness-lou.md) — the namesake; harness as action boundary, harness-as-policy.
- [Self-Harness](self-harness.md) — weakness-mine → minimal edit → regression-gated; most benchmark-bound.
- [HarnessFix](harnessfix.md) — step-level attribution (HTIR, 7 ETCLOVG layers) inside a known-failed trajectory.
- [RHO](rho.md) — benchmark-free; pure self-preference over re-solved past tasks.
- [Bayesian-Agent](bayesian-agent.md) — posterior over skills → patch/split/compress/retire/explore.
- [MOSS](moss.md) — source-level rewriting; production failure-replay; health-probe rollback.
- [What Makes a Harness a Harness](what-makes-a-harness.md) — operational definition + inclusion/exclusion test.
- [SkillHone](skillhone.md) — harness that persists decision history incl. rejected options.
- [HASP](hasp.md) — skills as **executable** Program Functions; runtime-control harness + policy-training + evolution; the auto-write/weight corner opposite to us.
- [SKILL.md Mining](skillmd-mining.md) — diagnostic **negative result**: trajectory-mined skill files are readable but don't transfer; learned components lose to a frequency prior. Inspectability ≠ improvement.

## B. Skill-as-trainable-state & self-evolving skill methods

- [SkillOpt](skillopt.md) — controllable text-space optimizer; held-out gate (Microsoft).
- [SkillGen](skillgen.md) — skills as interventions; causal repair-vs-regression.
- [SkillLens](skilllens.md) — full lifecycle; negative transfer; self-eval ≈46.4%.
- [Trace2Skill](trace2skill.md) — distill parallel trajectories into a skill directory (Qwen).
- [EvoSkill](evoskill.md) — failure-driven discovery; Pareto selection.
- [MUSE-Autoskill](muse-autoskill.md) — full skill lifecycle; unit-tested skills.
- [SkillEvolver](skillevolver.md) — meta-skill refining post-deployment; silent-bypass audit.
- [SkillAdaptor](skilladaptor.md) — step-level attribution + acceptance-gated, weight-free updates.
- [Socratic-SWE](socratic-swe.md) — trace-derived skills steer a self-evolving SWE curriculum.
- [EmbodiSkill](embodiskill.md) — disambiguates flawed-skill vs. execution-lapse before revising.
- [Skill-MAS](skill-mas.md) — orchestration as an evolvable meta-skill; held-out gate.
- [SkillHarness](skillharness.md) — safe skills for computer-use agents; macro/micro split, risk-guard activation, evidence-gated sparse updates ("curate, not grow"); the name collision.
- [OpenClaw-Skill](openclaw-skill.md) — Collective Skill Tree Search; multi-model judges score quality + **cross-model transferability**; CSRL selects multiple skills to avoid collapse.

## C. Skill retrieval & selection at scale

- [SkillDAG](skilldag.md) — typed, conflict-aware skill graph; queried + evolved at inference.
- [Graph-of-Skills](graph-of-skills.md) — inference-time budgeted, dependency-aware retrieval (offline graph + reverse-aware PPR).
- [SkillGraph](skillgraph.md) — typed skill graph co-evolved with the policy via RL (graph + GRPO); distinct from SkillDAG.
- [SGDR](sgdr-web-agents.md) — stepwise, state-grounded retrieval for web agents.

## D. Self-evolving agents & memory

- [TMEM](tmem.md) — parametric memory (LoRA weights online) — the weight-based counter-example.
- [APEX](apex.md) — exploration collapse + strategy map.
- [Do Self-Evolving Agents Forget?](self-evolving-forget.md) — non-monotonic self-evolution.
- [SkillOS](skillos.md) — learning skill curation.
- [SAGE](sage.md) — self-evolving agentic graph-memory engine.
- [EXG](exg.md) — self-evolving agents with experience graphs.

## E. Framing, surveys & infrastructure

- [Externalization in LLM Agents](externalization-review.md) — the umbrella survey; harness = unification layer.
- [Agent Skill Evaluation and Evolution](agent-skill-eval-survey.md) — four evolution paradigms; six benchmark categories.
- [SkillWiki](skillwiki.md) — wiki-style infrastructure; provenance-aware evolution.
- [Skill-Harnessing RA](skill-harnessing-ra.md) — 10 patterns + 4-layer reference architecture for skill-mediated agents; harnessing-vs-management split; most invariants map to a named pattern.

## F. Foundational context

- [Voyager](voyager.md) — executable skill library (2023).
- [Reflexion](reflexion.md) — verbal reinforcement learning (2023).
- [TextGrad](textgrad.md) — automatic "differentiation" via text (2024).
- [GEPA](gepa.md) — reflective prompt evolution can outperform RL (2025).

## G. Adjacent: fuzz-driver / fuzzing-harness generation (reference only)

A different "harness" (fuzz drivers); kept for the output-quality-validation lesson — see [synthesis/ecosystem-heat.md](../../synthesis/ecosystem-heat.md).

- [QuartetFuzz](quartetfuzz.md) · [Agentic Fuzzing](agentic-fuzzing.md) · [MASFuzzer](masfuzzer.md) · [Multi-Agent Java Harness](java-fuzz-harness.md) · [STITCH](stitch.md) · [HarnessAgent](harnessagent.md) · [FalseCrashReducer](falsecrashreducer.md) · [Scheduzz](scheduzz.md) · [Reliable LLM Fuzz Testing (vision)](reliable-fuzz-vision.md) · [SEC-bench Pro](sec-bench-pro.md)
