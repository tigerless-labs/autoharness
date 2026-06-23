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

This layer is a seam: the static path is built to ship and run without it. Whether outcome signal —
usage telemetry, conflict-as-interference (see [management.md](management.md)), outcome-driven retire
or evolve — is later folded into the active path is left open, not ruled out; it switches on once the
ledger and telemetry are rich enough to earn it. Reserving it first keeps the static manager shippable
without foreclosing either evolution or pulling outcome signal forward.
