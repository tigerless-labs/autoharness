# SkillHone — a harness for continual evolution via decision history

**Li, Hu** — "SkillHone: A Harness for Continual Agent Skill Evolution Through Persistent Decision History" ([arXiv:2606.08671](https://arxiv.org/abs/2606.08671), 2026-06).

Problem: existing approaches improve skills only within bounded runs and "retain only the final artifact, discarding the decision history" — so future agents can't see earlier revisions, evaluations, or rejected options. SkillHone is a **harness** anchored in persistent decision history:
- Couples skill revisions with evaluation-side evidence that supplies practice feedback.
- Records structured logs of diagnoses, revisions, evidence, and outcomes.
- **Role-separated subagents** test candidates on practice probes with **redacted reporting** and propose revisions informed by past decisions.
- Enables cross-session refinement without rediscovering past rationale.

Results: deep-research benchmarks in a raw open-web setting (no integrated search stack), Qwen3.6-35B-A3B backbone — **+15.8 on GAIA**, +3.2 on WebWalkerQA-EN; also beats prior skill-evolution methods.

**Relevance to autoharness:** the most direct harness-engineering peer in this collection — treats the **harness itself as the locus of improvement** and persists *process* (including rejected alternatives), not just the final skill. Role separation + redacted feedback are concrete guardrail patterns; persisting rejected options is exactly the audit trail autoharness's rollback story needs.
