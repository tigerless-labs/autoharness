# The AutoHarness paper (the namesake)

**Lou, Lázaro-Gredilla, Dedieu, Wendelken, Lehrach, Murphy — "AutoHarness: improving LLM agents by automatically synthesizing a code harness"** ([arXiv:2603.03329](https://arxiv.org/abs/2603.03329), 2026, Google DeepMind-affiliated).

Not fuzzing. The harness is the agent's **action boundary / immune system**: a code layer that filters environment-illegal actions, and can escalate to a full code-policy.

Core claims:
- Motivation: in Kaggle GameArena chess, **78% of Gemini-2.5-Flash losses were illegal moves**, not strategy.
- Method: the LLM **synthesizes its own code harness** via a few rounds of iterative code refinement from environment feedback; the LLM acts as a mutation operator in a program-space search.
- Result: harness prevents all illegal moves across **145 TextArena games**; the smaller Flash + harness beats the larger Gemini-2.5-Pro.
- Limit case — **harness-as-policy**: generate the entire policy as code, no LLM call at decision time. Code-policy beats Gemini-2.5-Pro and GPT-5.2-High on 16 single-player games, cheaper.
- Headline: a small model synthesizing a custom harness (or full code-policy) can outperform a much larger model.

**Gap it leaves:** validated only in TextArena (clear rules, instant feedback, decidable legality). Moving "feedback → harness-code iteration" to sparse-feedback, fuzzy-legality real tasks (API calls, desktop, codebases) is the open problem — and a natural wedge. No official code released.
