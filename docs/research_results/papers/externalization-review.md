# [论文] Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering

**Zhou, Chai, Chen, … Lin, Zhang (21 authors)** — "Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering" ([arXiv:2604.08224](https://arxiv.org/abs/2604.08224), 2026-04, 54pp).

The umbrella survey for this whole collection. Thesis: modern agents are built "less by changing model weights than by reorganizing the runtime around them" — capability is **externalized** into infrastructure (the cognitive-artifacts framing), tracing a progression *weights → context → harness*.

Four coupled forms of externalization:
- **Memory** — externalizes state across time.
- **Skills** — externalizes procedural expertise.
- **Protocols** — externalizes interaction structure.
- **Harness engineering** — the *unification layer* that coordinates the other three into governed execution.

Key claims: infrastructure isn't glue — it "transforms hard cognitive burdens into forms the model can solve more reliably"; the parametric-vs-externalized trade-off is the central design axis; emerging frontier is **self-evolving harnesses and shared agent infrastructure**, with open problems in evaluation, governance, and model–infrastructure co-evolution.

**Relevance to autoharness:** names the harness as a first-class engineering concern and the coordinating layer — direct vocabulary for positioning autoharness as a *self-evolving harness*. Use as the framing citation.
