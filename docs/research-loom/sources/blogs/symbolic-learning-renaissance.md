# [博客] 符号学习在 Agent 时代的文艺复兴？ (The Symbolic-Learning Renaissance in the Agent Era)

**Eddy (Zhihu)** — [zhuanlan.zhihu.com/p/2044779283978139242](https://zhuanlan.zhihu.com/p/2044779283978139242) · login-walled (content supplied by user). The framing essay that ties this whole corpus together.

**Thesis:** [AutoHarness](../papers/autoharness-lou.md) + [SkillOpt](../papers/skillopt.md) + Heuristic Learning (+ community skills/memory work) all point at a return of *symbolic learning* — not old expert systems, but **symbols as trainable external state**.

Compression lens (the load-bearing idea):
- A symbol = a discrete, reusable, composable, **grounded** handle that compresses action-relevant invariants. Good compression = intelligence (MDL / Kolmogorov / Solomonoff lineage).
- A trajectory summarized into a skill / a piece of code / a test **is** symbolic learning.
- Deep learning: `experience → gradient → weights`. This line: `experience → reflection/search/edit → symbolic artifact`.

Why old symbolic AI failed: not because symbols were wrong, but **maintenance cost** (grounding, open world, rule-base tech debt). The bet now: **coding agents change the maintenance-cost curve** of symbolic systems.

Three representative works it names: **Heuristic Learning** ([Jiayi Weng blog](learning-beyond-gradients.md)), **AutoHarness** (symbol layer as action boundary), **SkillOpt** ("gradient descent in symbol space": rollout = forward, reflection = backward, held-out gate = validation).

**Relevance to autoharness:** the thesis statement for the project. **Caveat it raises (the autoharness wedge):** the symbol layer is not free — skills bloat, harnesses overfit, memory pollutes decisions, agents game the verifier. The scarce capability is **auto abstract / dedup / compress / refactor / verify / delete** — maintaining the symbol ecosystem, not just growing it (the maintain-not-grow invariant).
