# eval — the reserved evaluation layer

Reserved. The active path (intake → manage → retrieve) runs without this layer; it accumulates the
signal a future evolution layer will stand on. Spine: [workflow.md](workflow.md).

## Per-skill rationale ledger

Every skill carries, attached to it, the reason it was born and the reason for each later update.
This ledger is the skill's own evaluation record — not a score, but the accumulated *why* behind its
existence and its changes. It is the foundation of evolution: a future layer can only judge whether a
skill still earns its place if the original and revised intent are on record. Its lightweight form
borrows **SkillHone** (Tencent): persist the decision history — diagnoses, revisions, and **rejected
options** — beside each skill, so history attaches as an audit trail without a heavy evaluation
apparatus.

## Usage telemetry

The agent platform's skill-usage monitoring (e.g. Anthropic's) is a second, external data source —
how often and where each skill actually fires. It informs future update and retire decisions without
being part of the active structural path.

## Reservation constraint

This layer is a seam, not a spine. The active path must never require it. Conflict-as-interference
(see [management.md](management.md)) and any outcome-driven retire or evolve action belong here,
switched on only once the ledger and telemetry are rich enough to drive them — so shipping the static
manager first does not foreclose evolution later.
