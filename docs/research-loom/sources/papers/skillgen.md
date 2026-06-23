# [论文] SkillGen: Verified Inference-Time Agent Skill Synthesis

**(authors not captured)** — [arXiv:2605.10999](https://arxiv.org/abs/2605.10999) · 2026-05 · code: [yccm/SkillGen](https://github.com/yccm/SkillGen) (~10★).

Key idea: model skills as **interventions** for causal verification — compare the same instances with and without the skill, counting both repairs **and** regressions. Contrastive induction over success + fail trajectories.

**Relevance to autoharness:** the intervention framing is the right way to answer "is the *net* effect of this change positive?" rather than "how many failures did it fix?" — the repair-vs-regression accounting autoharness's gate needs.
