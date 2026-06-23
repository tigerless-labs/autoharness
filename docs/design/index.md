# design — index

The design of autoharness: a structural manager for the agent skill layer. Pain points and intent
live in [`../DEFINITION.md`](../DEFINITION.md).

- **[workflow.md](workflow.md)** — the spine: principle, the four-layer pipeline (intake → manage →
  retrieve, with a reserved eval layer), provisional working hypotheses, and what each layer borrows.
- **[management.md](management.md)** — the typed DAG: relations, conflict, dedup, and the admission
  gate for new skills.
- **[eval.md](eval.md)** — the reserved evaluation layer: the per-skill rationale ledger and the
  usage-telemetry data source that found a future evolution layer.
