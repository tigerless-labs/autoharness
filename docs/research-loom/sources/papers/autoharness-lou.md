# [论文] AutoHarness: Improving LLM Agents by Automatically Synthesizing a Code Harness

**Lou, Lázaro-Gredilla, Dedieu, Wendelken, Lehrach, Murphy (Google DeepMind-affiliated)** — [arXiv:2603.03329](https://arxiv.org/abs/2603.03329) · 2026-02 · no public code. **The namesake** (not fuzzing).

The harness is the agent's **action boundary / immune system**: a code layer that filters environment-illegal actions and can escalate to a full code-policy.

- Motivation: in Kaggle GameArena chess, **78% of Gemini-2.5-Flash losses were illegal moves**, not strategy.
- Method: the LLM **synthesizes its own code harness** through a few rounds of iterative code refinement from environment feedback — the LLM acting as a mutation operator in a program-space search.
- Result: harness prevents all illegal moves across **145 TextArena games**; smaller Flash + harness beats the larger Gemini-2.5-Pro.
- Limit case — **harness-as-policy**: generate the entire policy as code, no LLM call at decision time. Code-policy beats Gemini-2.5-Pro and GPT-5.2-High on 16 single-player games, cheaper.

**Relevance to autoharness:** the namesake and conceptual anchor. **Gap it leaves:** validated only in TextArena (clear rules, instant feedback, decidable legality). Moving "feedback → harness-code iteration" to sparse-feedback, fuzzy-legality real tasks (API calls, desktop, codebases) is the open problem — and autoharness's natural wedge.
