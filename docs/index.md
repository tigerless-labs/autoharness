# docs — autoharness documentation map

Single entry point for the `docs/` tree. Each fact lives in exactly one place; this index
only points. Keep it current when files are added, moved, or removed.

## Foundations (the *what* and *why* of the project)

- [DEFINITION.md](DEFINITION.md) — single authoritative project definition.
- [DECISION.md](DECISION.md) — technical-selection decision record.

## Design — architecture and the *why*

- [design/](design/index.md) — design-doc index. Start at the spine
  ([design/workflow.md](design/workflow.md): principle + pipeline + invariants).

## Working artifacts

- [plans/](plans/index.md) — per-change implementation plans (exempt from design-doc style rules).
- [TODO.md](TODO.md) — tracked follow-ups not yet on the roadmap.
- [testing.md](testing.md) — test conventions and the per-file test map.

## Research

- [research_results/](research_results/index.md) — per-source reference library for the agent-harness /
  symbolic-learning landscape (research notes, not design docs). One source = one card, split into
  [papers/](research_results/papers/index.md), [github/](research_results/github/index.md),
  [blogs/](research_results/blogs/index.md), and [synthesis/](research_results/synthesis/index.md).
