# [GitHub] affaan-m/ECC

[github.com/affaan-m/ECC](https://github.com/affaan-m/ECC) (~212k★) · curated skill pack **with** an opt-in learning loop.

The key counter-example to "optimizers can't be popular." Mostly a curated pack, but ships a real loop: **Instincts (Continuous Learning v2)** — hooks auto-extract patterns into confidence-scored "instincts"; `/evolve` clusters them into skills (work → extract → score → promote). Plus `/skill-create` from git history, SessionStart/End memory hooks. (v1 used a Stop-hook to observe; v2 moved observation to PreToolUse/PostToolUse for 100% capture.)

## Skill / experience accumulation flow (verified 2026-06-23)

The full loop, two-tier (cheap always-on **instincts** → promoted **skills**), with a clean split between the **use/forward** path and the **improve/reverse** path:

1. **Observe (capture).** `observe.sh` on **PreToolUse / PostToolUse** hooks + a background **Haiku observer** analysing in parallel. Hook-driven = **100% deterministic capture** (the stated reason for moving off v1's skill/Stop-hook observation, which "fires ~50–80% of the time"). Project detected via `~/.claude/homunculus/projects.json`.
2. **Distil → stage (optimistic write, no gate).** Patterns become **atomic instincts** written to a **staging store outside `.claude/`**: `CLV2_HOMUNCULUS_DIR` (default `~/.local/share/ecc-homunculus`); per-project at `~/.claude/homunculus/projects/<id>/instincts/personal/`. Each instinct: Action + Evidence + Examples; **confidence ≈0.3–0.85 (by frequency)**; **domain tag** (code-style/testing/git/debugging/workflow/file-patterns); **scope** project|global.
3. **Curate (rolling, not one-shot).** **Confidence decay if contradicted**; project→global promotion. This is the only "conflict" handling — heuristic scoring, **no structural conflict scan**.
4. **Use / inject (forward path).** **SessionStart + UserPromptSubmit** hooks inject **project-scoped** instincts into context, **char-capped** (`ECC_SESSION_START_MAX_CHARS` default 8000; `…_CONTEXT=off` disables; `ECC_HOOK_PROFILE`/`ECC_DISABLED_HOOKS` gate). 100% fire. Purpose is **to apply, not to optimize** — but applying produces the adherence evidence step 3 consumes. *(Open: within-project, top-N-by-confidence vs all-to-cap, and whether UserPromptSubmit relevance-filters by prompt — needs reading `scripts/hooks/`.)*
5. **Evolve → promote (gated entry to the live skill layer).** `/evolve` clusters high-confidence instincts into **skills/commands** at `$ECC_AGENT_DATA_HOME/skills/learned/` (default root `~/.claude`). `/skill-create` also mints skills from git history. `/instinct-import` · `/instinct-export` move instincts in/out.
6. **Skill-layer maintenance (periodic, manual — the "A" route).** `/skill-stocktake` audits skills (overlap / staleness / usage → **Keep/Improve/Update/Retire/Merge**, destructive needs confirm; Quick re-checks only changed via `results.json`+mtime). `rules-distill` lifts cross-skill principles (in 2+ skills) into **rules**, human-approved. Philosophy: **"deterministic collection + LLM judgment"** and **"What, not How"**.
7. **Skill use.** Promoted skills then ride **native description-relevance triggering (~50–80%)** — which is *why* must-always-apply behaviour is deliberately kept as **hook-injected instincts (100%)**, not skills.

**Two reliability tiers (the load-bearing design choice):** instinct→hook = **100%** deterministic; skill→description = **50–80%** model-judged. ECC routes high-reliability rules to hooks and reserves the skill path for "occasionally relevant."

```
PreTool/PostTool hooks ─► instincts (staging: ~/.local/share/ecc-homunculus, conf+domain+scope)
   observe                    │  decay-if-contradicted · project→global
                              ├─► USE: SessionStart/UserPromptSubmit inject (project-scoped, ≤8000 chars, 100%)
                              └─► /evolve ─► skills/learned/ ─► description-trigger (~50–80%)
                                            skill-stocktake · rules-distill (periodic, human-approved)
```

**Mapping to autoharness:** the **reverse/improve** half (distil · curate · evolve · stocktake · rules-distill) is our territory (Intake + Manage); the **forward/use** half (inject/trigger) is host-native — we shape artifacts, the host applies. Borrow: "deterministic collection + LLM judgment", incremental re-scan (changed-only), the Keep/Improve/Update/Retire/Merge verdict set, staging-outside-`.claude` + gated promotion, and the **vehicle-by-reliability** rule (skill vs hook vs always-loaded). Don't inherit: ECC has **no structural dedup/conflict gate** (overlap only, periodic, manual) — that gated, conflict-aware admission is our wedge.

**Relevance to autoharness:** the category wins when packaged as "install-and-it-works content pack + an optional learning loop hidden inside," not as a research framework. ECC owns the **distribution** corner; [SkillOpt-Sleep](microsoft-skillopt-sleep.md) owns engineering, [RHO](../papers/rho.md) owns validation method — nobody has all three.
