# Paper collection — agent skills, meta-skills & harness evolution (2026-06-22)

A focused reading list shared 2026-06-22: the April–June 2026 wave on **externalized skills,
meta-skills, and self-evolving harnesses**. One file per source; each is a standalone summary
(core problem · method · results · relevance to autoharness). Links are arXiv submission pages
and, where released, code.

This is a *deeper, per-paper* read that complements the prior compressed landscape in
[../index.md](../index.md) — overlaps (e.g. MUSE-Autoskill) are cross-linked, not duplicated.

## A. Framing, surveys & infrastructure

1. [externalization-review.md](externalization-review.md) — *Externalization in LLM Agents* ([2604.08224](https://arxiv.org/abs/2604.08224)). The umbrella survey: memory/skills/protocols/**harness** as the four externalized layers; harness = the unification layer.
2. [agent-skill-eval-survey.md](agent-skill-eval-survey.md) — *Agent Skill Evaluation and Evolution* ([2606.11435](https://arxiv.org/abs/2606.11435), [code](https://github.com/Cassie07/AgentSkill_Survey)). Four evolution paradigms; six benchmark categories; the evaluation-gap map.
3. [skillwiki.md](skillwiki.md) — *SkillWiki* ([2606.16523](https://arxiv.org/abs/2606.16523), [code](https://github.com/Huangdingcheng/SkillWiki)). Wiki-style infrastructure for skill production, governance, and provenance-aware evolution.
4. [claude-code-skills.md](claude-code-skills.md) — *Lessons from building Claude Code* ([blog](https://claude.com/blog/lessons-from-building-claude-code-how-we-use-skills)). Production practice: nine skill categories, Gotchas as highest-signal content, descriptions as trigger specs.

## B. Meta-skills & self-evolving skill methods

5. [skill-mas.md](skill-mas.md) — *Skill-MAS* ([2606.18837](https://arxiv.org/abs/2606.18837), [code](https://github.com/linhh29/Skill_MAS)). Orchestration as an evolvable **Meta-Skill**; multi-trajectory rollout + selective reflection; held-out gate.
6. [skillevolver.md](skillevolver.md) — *SkillEvolver* ([2605.10500](https://arxiv.org/abs/2605.10500)). Meta-skill that refines **after deployment** from others' failures; fresh-agent overfit + silent-bypass audit.
7. [muse-autoskill.md](muse-autoskill.md) — *MUSE-Autoskill* ([2605.27366](https://arxiv.org/abs/2605.27366)). Full skill lifecycle (create/memory/manage/evaluate) with unit-tested, experience-aware skills.
8. [skilladaptor.md](skilladaptor.md) — *SkillAdaptor* ([2606.01311](https://arxiv.org/abs/2606.01311), [code](https://github.com/zjunlp/SkillAdaptor)). **Step-level** failure attribution + acceptance-gated, weight-free updates.
9. [socratic-swe.md](socratic-swe.md) — *Socratic-SWE* ([2606.07412](https://arxiv.org/abs/2606.07412)). Trace-derived skills steer a self-evolving SWE **curriculum**; 50.4% on SWE-bench Verified.
10. [embodiskill.md](embodiskill.md) — *EmbodiSkill* ([2605.10332](https://arxiv.org/abs/2605.10332)). Disambiguates **flawed skill vs. execution lapse** before revising; embodied setting.

## C. Skill retrieval & selection at scale

11. [skilldag.md](skilldag.md) — *SkillDAG* ([2606.03056](https://arxiv.org/abs/2606.03056), [code](https://github.com/Ericbai06/SkillDAG)). Typed, conflict-aware skill graph queried and evolved at inference time; holds up as the pool scales 10×.
12. [sgdr-web-agents.md](sgdr-web-agents.md) — *SGDR* ([2606.04391](https://arxiv.org/abs/2606.04391), [code](https://github.com/plusnli/skill-dynamic-retrieval)). Stepwise, **state-grounded** retrieval for web agents; skills bound to runtime page state.

## D. Harness for continual evolution

13. [skillhone.md](skillhone.md) — *SkillHone* ([2606.08671](https://arxiv.org/abs/2606.08671)). Harness that persists **decision history** (incl. rejected options); role-separated subagents, redacted feedback; +15.8 GAIA.

---

**Threads that recur across the collection** (the design questions autoharness must answer):
- **Net-effect gating, not failure-count.** Held-out validation (Skill-MAS), acceptance checks (SkillAdaptor), unit tests (MUSE) — accept an edit only if it strictly helps.
- **Attribution before editing.** Step-level fault localization (SkillAdaptor), skill-vs-lapse disambiguation (EmbodiSkill), silent-bypass detection (SkillEvolver) — don't rewrite a rule that failed because it was ignored.
- **Persist process, not just the artifact.** Decision history + rejected alternatives (SkillHone) — the audit trail that makes rollback meaningful.
- **Conflict-aware structure at scale.** Typed conflict edges (SkillDAG) once rules multiply.
- **Weight-free & portable.** Every method here learns the *document*, not the weights — transferable across models and harnesses.
