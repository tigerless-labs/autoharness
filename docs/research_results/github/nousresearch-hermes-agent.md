# [GitHub] NousResearch/Hermes-Agent

[github.com/NousResearch/Hermes-Agent](https://github.com/NousResearch/Hermes-Agent) · open-source agent with memory + self-learning.

Autonomous **skill creation after complex tasks**; skills self-improve in use; periodic memory nudges (interval 10); FTS5 session search + LLM summarization; a `memory` tool (add/replace/remove) with capacity-driven consolidation; [Honcho](plastic-labs-honcho.md) user modeling. Also feeds back to the model level: batch trajectory generation + trajectory compression to train next-gen tool-calling models.

**Relevance to autoharness:** a shipped example of in-use skill self-improvement and bounded memory consolidation — the add/replace/remove + capacity-driven consolidation is the maintain-not-grow behavior in production.
