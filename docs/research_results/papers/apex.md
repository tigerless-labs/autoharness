# [论文] APEX: Autonomous Policy Exploration for Self-Evolving LLM Agents

**(authors not captured)** — [arXiv:2605.21240](https://arxiv.org/abs/2605.21240) · 2026-05 · no public code.

Warns of **exploration collapse**: as memory grows, behavior concentrates on familiar high-reward routines — worse when there is no benchmark to reveal better options. Proposes a strategy map to keep exploring.

**Relevance to autoharness:** direct evidence for the **exploration-budget invariant** — a benchmark-free optimizer ([RHO](rho.md)) is exactly the regime where collapse bites hardest, so an explicit exploration budget is mandatory, not optional.
