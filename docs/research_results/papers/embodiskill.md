# [论文] EmbodiSkill: Skill-Aware Reflection for Self-Evolving Embodied Agents

**Ju, Wang, Ding, Yang, … Cao (15 authors)** — "EmbodiSkill: Skill-Aware Reflection for Self-Evolving Embodied Agents" ([arXiv:2605.10332](https://arxiv.org/abs/2605.10332), 2026-05).

Problem: embodied agents must evolve skills from their own trajectories, but digital-domain methods give "coarse skill updates," and a failed task is ambiguous — it may reflect **flawed skill content** *or* an **execution lapse** (agent ignored valid guidance). EmbodiSkill is a training-free framework that disambiguates: interpret each trajectory against the current skill, use *skill-changing* evidence to revise the skill body, and use *execution-lapse* evidence to preserve and emphasize the guidance that was already correct.

Results: ALFWorld + EmbodiedBench — consistent success gains. On ALFWorld a frozen Qwen3.5-27B executor reaches **93.28%**, beating GPT-5.2 used directly (no skills) by 31.58%.

**Relevance to autoharness:** the **"bad skill vs. ignored skill" distinction** is the crucial attribution guardrail — autoharness must not rewrite a harness rule that failed only because it was never followed (cf. SkillEvolver's silent-bypass audit). Embodied setting, but the attribution logic is domain-general.
