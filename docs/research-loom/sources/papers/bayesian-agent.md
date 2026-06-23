# [论文] Bayesian-Agent: Posterior-Guided Skill Evolution for LLM Agent Harnesses

**(authors not captured)** — [arXiv:2606.08348](https://arxiv.org/abs/2606.08348) · 2026-06 · code: [DataArcTech/Bayesian-Agent](https://github.com/DataArcTech/Bayesian-Agent) (~27★).

Fixes "treating success/fail counts as reliable belief." Each skill/SOP is a hypothesis; maintain a **feature-conditioned posterior** over skills; map it to auditable actions **patch / split / compress / retire / explore**.

**Relevance to autoharness:** the posterior-over-skills framing turns raw outcome counts into a belief that *chooses a lever* — directly informs autoharness's attribution→action mapping (violation→enforce, scope-mismatch→generalize, conflict→retire, gap→gated-add). The explicit `explore` action pairs with [APEX](apex.md)'s exploration-collapse warning.
