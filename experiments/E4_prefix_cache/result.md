# E4 — prefix cache reusable across processes (hook ↔ host)?

## Question
Claim under test (asserted earlier, untested): an additive/external reflection step
launched from a hook "cannot reuse" the host's warm prompt cache, so its replay of the
turn would be cold (~full price). Is that true?

## Method
Call the same endpoint the host uses (`ANTHROPIC_BASE_URL` = local proxy `127.0.0.1:8790`)
with the claude.ai OAuth bearer (`~/.claude/.credentials.json`) + `anthropic-beta: oauth-*`.
Measure `usage.cache_read_input_tokens` vs `cache_creation_input_tokens`.

- **Part 1 (mechanism):** two *separate* python invocations send an identical ~6.8k-token
  prefix block (`cache_control: ephemeral`) on Haiku.
- **Part 2 (realistic):** replay a ~12k-token slice of THIS session's real transcript on
  Opus (the session model).

## Result
Part 1 — separate process fully reuses the cache:
```
call#1 (warm):  input=9  cache_creation=6825  cache_read=0
call#2 (reuse): input=9  cache_creation=0     cache_read=6825   # 100% hit
```
Part 2 — Opus returned HTTP 429 rate_limit (session is itself consuming the Opus budget);
not measured. Note it would NOT have hit the host cache anyway: the request carried only
transcript text, not Claude Code's exact system-prompt + tool-schema prefix, so the prefix
differs from byte 0.

## Conclusion (corrects the earlier claim)
- The **process / hook boundary is NOT a barrier.** Prompt cache is account-scoped and
  server-side; a second independent caller with a byte-identical prefix on the same account,
  same model, within TTL gets a full cache read. → A hook-launched reflection **can** ride a
  warm cache.
- The real variable is **prefix reconstruction**: a cache hit requires byte-identical prefix
  (system + tools + messages) + same model + same account + within TTL. The transcript gives
  messages but not the host's serialized system/tools, so a naive replay misses the *host's*
  cache; it still caches against the reflection layer's *own* stable prefix on repeat calls.
- Cost implication: reflection cost is ~cached-price (~0.1x input) when the prefix matches,
  not full price. The earlier "external layer ⇒ cold ⇒ near-full-price" pessimism was wrong.

evidence-for: docs/research-loom/ideas/episode-boundary-reflection.md (待解: 暖缓存可达性)
