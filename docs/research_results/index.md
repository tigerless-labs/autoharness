# Research results — autoharness landscape (as of 2026-06-10)

Compressed findings from the 2026-06-10 research session. Each file = one point.
These are research notes (citations + specifics are the value), not design docs —
the `docs/design/` style rules do not apply here.

1. [autoharness-paper.md](autoharness-paper.md) — what the namesake paper actually is
2. [symbolic-learning-framing.md](symbolic-learning-framing.md) — the "symbolic learning renaissance" thesis tying it together
3. [benchmark-free-optimization.md](benchmark-free-optimization.md) — how to define harness quality without a benchmark
4. [skill-learning-papers.md](skill-learning-papers.md) — the skill-as-trainable-state paper cluster
5. [oss-memory-self-learning.md](oss-memory-self-learning.md) — what shipped in open-source agents (incl. bootstrap)
6. [github-implementations.md](github-implementations.md) — which papers have code, and the name collision
7. [ecosystem-heat.md](ecosystem-heat.md) — skill packs vs optimizers, and how things go viral
8. [fuzzing-harness-adjacent.md](fuzzing-harness-adjacent.md) — the other "harness" (fuzz drivers), kept as reference

Reference lists:
- [paper-list.md](paper-list.md) — all referenced papers, grouped by theme, with arXiv links
- [github-list.md](github-list.md) — all referenced repos, grouped, with star counts

**One-line takeaway for autoharness's positioning:** the contested, low-competition
gap is *benchmark-free, trajectory-bootstrapped harness evolution with audit/gate/rollback* —
distinct from governance frameworks, fuzz-harness generation, and benchmark-requiring optimizers.
