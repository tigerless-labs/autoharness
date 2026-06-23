# [GitHub] openclaw/openclaw

[github.com/openclaw/openclaw](https://github.com/openclaw/openclaw) · docs at docs.openclaw.ai · the most complete open-source memory mechanism.

- Memory is plain Markdown on disk (no hidden state): `MEMORY.md` (long-term, curated) + `memory/YYYY-MM-DD.md` (daily).
- **Memory flush**: a silent turn before compaction reminds the agent to save important context. On by default.
- **Dreaming**: background cron consolidation; promotes short-term signals to `MEMORY.md` only past a **score + recall-frequency + query-diversity** gate; summaries to `DREAMS.md`, rollback-able.

**Relevance to autoharness:** the canonical on-disk symbol layer (and the basis MOSS evaluates on, 0.25→0.61). **Caveat:** Dreaming is **memory management, not harness validation** — its gate is *recall utility* (will this be retrieved again), not *net task improvement* (repairs > regressions on a replay set). No replay, no improvement test. It rhymes with the symbolic-learning line in shape only; it sits **off** the [validation-signal spectrum](../../synthesis/benchmark-free-validation.md).
