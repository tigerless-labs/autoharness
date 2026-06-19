# docs/design — architecture and the *why*

The design spine and per-step docs. Created as the design solidifies; keep this index current.
These docs obey the design-doc style rules in [CLAUDE.md](../../CLAUDE.md) (top-level design only,
ruthlessly concise, name modules/objects not functions/paths).

## Spine

- [workflow.md](workflow.md) — principle (maintain, don't grow) + the Observe→Detect→Attribute→
  Decide→Verify→Stage pipeline + the nine cross-cutting invariants. Start here.

## Steps

- [detect.md](detect.md) — observe (read-only) and isolate failure episodes on two channels
  (objective structural spine + user-correction overlay); the interrogative-exclusion filter.
- [attribute.md](attribute.md) — episode → responsible symbol and the four attribution classes
  (violation / scope-mismatch / gap / conflict); applicability and the omission half.
- [maintain.md](maintain.md) — value map → action set, the recurrence gate on addition, the
  per-action verify gate, the v1/v2 boundary, and staging.

## Evidence

The invariants rest on three measurements over real `~/.claude` records, under
[`experiments/`](../../experiments/): E1 (signal density), E2 (attribution feasibility),
E3 (applicability tractability).
