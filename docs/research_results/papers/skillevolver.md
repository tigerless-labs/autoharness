# SkillEvolver — skill learning as a meta-skill, from failures

**Zhang, Zhu, Zhou, Jia, Wang** — "SkillEvolver: A Meta-Skill for Online Skill Learning from Failures in Agent Self-Evolution" ([arXiv:2605.10500](https://arxiv.org/abs/2605.10500), 2026-05).

Problem: agent skills are static artifacts — "authored once… consumed unchanged, with no mechanism to improve from real use." SkillEvolver is a lightweight, plug-and-play **meta-skill** that repeatedly authors, deploys, and refines domain skills.

Distinguishing choices:
- Learning target is the skill's **prose and code, not weights** — output works in any agent, no retraining.
- The meta-skill is itself just a skill, loadable by any protocol-compliant CLI-agent.
- Unlike trace-distillation, refinement happens **only after deployment**, learning from failures a *different* agent hits while using the skill.
- A **fresh-agent overfit audit** detects leakage and deployment-specific failures, including a **silent-bypass mode** (skill looks valid but is never actually invoked).

Results: 83 SkillsBench tasks across 15+ domains — 56.8% vs. 43.6% (curated human skills) vs. 29.9% (no-skill). KernelBench GPU-kernel: mean speedup 1.16 → 1.51.

**Relevance to autoharness:** closest sibling to the harness wedge — post-deployment, failure-driven, weight-free, with an explicit **overfit/silent-bypass audit**. The silent-bypass check is a guardrail autoharness should adopt: an edit that is never exercised is not an improvement.
