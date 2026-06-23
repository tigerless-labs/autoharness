# workflow — the design spine

The governing principle, the four-layer pipeline, and the provisional working hypotheses behind them. Per-layer
docs and [index.md](index.md) hang off this. See [`../DEFINITION.md`](../DEFINITION.md) for pain
points and intent.

## Principle

**Manage the skill layer as a typed DAG, structurally.** A skill layer is not a flat pile; skills
relate, overlap, and contradict. Treating it as a typed relation graph turns conflict, redundancy,
and retrieval from judgement calls into structural operations computable from skill text alone — no
oracle, no outcome signal on the active path, no self-evaluation bias. Outcome signals are reserved
to the eval layer, which founds a later evolution layer but never gates the active path.

## Pipeline

```
 experience ─► Intake ─► Manage (typed DAG: relate · dedup · conflict · gated-add) ─► Retrieve
                              every skill ⟂ rationale ledger ─► (reserved) Eval
```

- **Intake** — new skills settle out of experience rather than being hand-authored. The accumulation
  engine is borrowed (ECC); intake's only obligation to the rest of the system is to present each
  candidate to the admission gate, never to write into the live layer directly.
- **Manage** — the typed DAG and its operations: induce relations, flag conflicts, cluster
  duplicates, and gate every addition. The heart of the system; see [management.md](management.md).
- **Retrieve** — return a bounded, dependency-complete subset for a task, surfacing prerequisites and
  conflict warnings flat similarity search cannot. Borrowed (Graph-of-Skills).
- **Eval (reserved)** — each skill carries the reason it was born and the reason for each update;
  that ledger, plus usage telemetry, is the foundation a future evolution layer stands on. Reserved:
  the active path must not depend on it. See [eval.md](eval.md).

## Working hypotheses (provisional — not yet ratified)

These are proposals, not settled invariants: the design is still being decided, and none carries
evidence yet. Treat each as something to validate or revise, not a fixed constraint. They become
invariants only once ratified and grounded.

1. **Skills are a typed DAG, not a flat pile.** Relations are first-class; everything downstream
   reads them.
2. **Structural-first.** Relations, conflict, dedup, and retrieval are computed from skill text, with
   no oracle and no outcome signal on the active path.
3. **Gated admission.** A candidate enters the graph only past a dedup check and a conflict check:
   overlap routes to merge or generalize, contradiction routes to resolution, neither-and-non-
   recurring routes to rejection.
4. **Conflict on the active path means contradiction.** It detects textual/logical opposition
   between skills; behavioural interference (co-use harm) needs outcomes and is reserved to eval.
5. **Structural edits are proposed, not silent.** Merges of look-alikes and conflict resolutions are
   reviewable proposals a human confirms — never an automatic rewrite, because text similarity alone
   cannot tell a redundant clone from a legitimate parallel specialist.
6. **Every skill carries its rationale ledger.** Birth and each update record their reason; this is
   the reserved evolution foundation.
7. **Retrieval returns a bounded, dependency-complete set**, not a flat top-k.
8. **The eval layer is reserved.** Intake → Manage → Retrieve must run without it; it accumulates now
   and drives decisions only in a future evolution layer.

## What each layer borrows

Intake ← ECC (accumulation). Manage ← SkillDAG (typed graph, conflict/duplicate edges) + SkillReducer
(semantic dedup). Retrieve ← Graph-of-Skills (budgeted, dependency-aware). The uncovered ground this
project owns: running the whole loop over the **real prose symbol layer** rather than structured
benchmark skills, and the per-skill rationale ledger.
