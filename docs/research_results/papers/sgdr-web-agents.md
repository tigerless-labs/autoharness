# [论文] Online Skill Learning for Web Agents via State-Grounded Dynamic Retrieval (SGDR)

**Li, Deng, Wang, Huang, Shi, Tan, Lu, Liu** — "Online Skill Learning for Web Agents via State-Grounded Dynamic Retrieval" ([arXiv:2606.04391](https://arxiv.org/abs/2606.04391), 2026-06, 17pp). Code: [plusnli/skill-dynamic-retrieval](https://github.com/plusnli/skill-dynamic-retrieval).

Problem: existing online skill learning retrieves a fixed skill set from the **initial instruction** and holds it constant — misaligned with web execution, where "the appropriate next action depends not only on the task goal but also on the current webpage state." SGDR (State-Grounded Dynamic Retrieval) enables **stepwise** reuse:
- Sliding-window extraction turns completed trajectories into reusable sub-procedures usable at intermediate states.
- Dual **text-code** representation links retrieval to executable actions.
- State-grounded retrieval matches skills to *both* goal and current page state.

Results: WebArena (5 domains) — 37.5% with GPT-4.1, 24.3% with Qwen3-4B; +10.6% / +10.0% relative over the strongest baseline.

**Relevance to autoharness:** retrieval keyed to **runtime state**, not just the task — a reminder that harness behavior is state-dependent, and that skills/rules should bind to the situation they apply in. Sub-trajectory extraction is a granularity option for trajectory-bootstrapping.
