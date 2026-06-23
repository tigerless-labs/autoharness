# [GitHub] All-Hands-AI/OpenHands

[github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands) · open-source coding agent.

The thinnest of the memory-equipped agents: automatic context compression, a skills directory, and `AGENTS.md` repo memory. **No documented auto-update or experience-learning loop.**

**Recall is pure-file / keyword — no vector retrieval.** Microagents/skills (`.openhands/microagents/` → v1 `skills/`) are selected by **literal keyword substring match** (`match_trigger`: `keyword.lower() in message`); trigger-less repo skills are always-injected, triggered ones disclosed by name then injected on match (+ an LLM-invoked `invoke_skill` path). History is handled by **condensers** (recency-drop / LLM-summarization) — never embeddings. A `chromadb`+`llama_index` `LongTermMemory` existed in v0 but was **dead, opt-in code with zero call-sites**, and is **entirely removed in the v1 SDK** (0 hits for embed/vector/chroma/faiss). *evidence:* `software-agent-sdk` `skills/trigger.py`, `skills/skill.py`, `context/condenser/`.

**Relevance to autoharness:** the baseline — a widely-used agent that has the *substrate* (skills dir, repo memory) but no learning loop on top. Exactly the gap autoharness fills.
