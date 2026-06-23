# [论文] Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills

**Xiao, Jiao, Wang, Wang, Zhao, Wei, Zhang, Qu** — "Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills" ([arXiv:2606.07412](https://arxiv.org/abs/2606.07412), 2026-06).

Problem: training SWE agents is bottlenecked by scarce high-quality tasks; fixed mutation / bug-injection synthesis produces task distributions disconnected from the agent's actual weaknesses. Socratic-SWE is a closed loop that recycles the agent's own solving **traces** as training signal — distilling them into structured agent skills that capture recurring failures and repair patterns, then using those skills to **generate targeted repair tasks in real repos**.

Loop: candidate tasks pass execution-based validation → scored by a **solver-gradient alignment reward** (keep tasks both verifiable and useful) → updated solver generates new traces → curriculum adapts each round.

Results: SWE-bench Verified/Lite/Pro, Terminal-Bench 2.0 — consistently beats self-evolving baselines at equal compute; **50.40% on SWE-bench Verified after three iterations**.

**Relevance to autoharness:** demonstrates traces as "a scalable substrate for self-evolving agents" — the same trajectory-bootstrapping premise, applied to curriculum rather than harness. The solver-gradient-alignment filter (keep only *useful* derived artifacts) is a selection idea worth porting.
