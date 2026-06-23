# [GitHub] NousResearch/Hermes-Agent

[github.com/NousResearch/Hermes-Agent](https://github.com/NousResearch/Hermes-Agent) · open-source agent with memory + self-learning.

Autonomous **skill creation after complex tasks**; skills self-improve in use; periodic memory nudges (interval 10); FTS5 session search + LLM summarization; a `memory` tool (add/replace/remove) with capacity-driven consolidation; [Honcho](plastic-labs-honcho.md) user modeling. Also feeds back to the model level: batch trajectory generation + trajectory compression to train next-gen tool-calling models.

**Recall is pure-file / keyword — no vector retrieval (by default).** Skills under `~/.hermes/skills/<cat>/<name>/SKILL.md` are selected by **3-level progressive disclosure**: Level-0 descriptor index (name+description) in the prompt → `skill_view(name)` loads the body on demand → `skill_view(name, path)` for a reference; the LLM picks by reading descriptors (no similarity step). Memory = two always-injected flat files (`MEMORY.md` ~2200 char, `USER.md` ~1375 char, frozen snapshot for prefix-cache); past-chat recall = **FTS5 keyword** search over a SQLite SessionDB (docs: *"Keyword only, no vector/semantic"*). Vector/embeddings exist only as **open proposals** (issues #346/#531/#844/#10355) and **optional external plugins** (Honcho/Mem0/Chroma-skill), never the default path.

**Relevance to autoharness:** a shipped example of in-use skill self-improvement and bounded memory consolidation — the add/replace/remove + capacity-driven consolidation is the maintain-not-grow behavior in production.
