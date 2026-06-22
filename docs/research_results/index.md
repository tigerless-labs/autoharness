# Research results — autoharness landscape

Per-source reference library for the 2026 agent-harness / symbolic-learning landscape. **One source = one card**; each card's title tags it `[论文]` / `[GitHub]` / `[博客]`, names the work and its authors/org, links the source, and summarizes it with relevance to autoharness. Research notes (citations + specifics are the value) — the `docs/design/` style rules do not apply here.

## Layout

- **[papers/](papers/index.md)** — `[论文]` cards (44), grouped: core harness line · skill-as-state · retrieval/selection · self-evolving memory · surveys/infra · foundational · fuzzing-adjacent.
- **[github/](github/index.md)** — `[GitHub]` cards for non-paper-code repos: OSS agents, skill packs, the three "AutoHarness" name-collisions, trending projects (+ official-implementation index).
- **[blogs/](blogs/index.md)** — `[博客]` cards: the symbolic-learning thesis, Heuristic Learning, the Claude Code skills blog, the 1k-experiments log.
- **[synthesis/](synthesis/index.md)** — the cross-source analysis no single card owns: the [benchmark-free validation spectrum](synthesis/benchmark-free-validation.md) and [ecosystem heat / positioning](synthesis/ecosystem-heat.md).

## Where to start

1. [AutoHarness (Lou et al.)](papers/autoharness-lou.md) — the namesake and its open gap.
2. [Symbolic-Learning Renaissance](blogs/symbolic-learning-renaissance.md) — the thesis tying the corpus together.
3. [Defining harness quality without a benchmark](synthesis/benchmark-free-validation.md) — how to gate edits with no oracle.
4. [Ecosystem heat & positioning](synthesis/ecosystem-heat.md) — the name collision and the wedge.

**One-line takeaway for autoharness's positioning:** the contested, low-competition gap is *benchmark-free, trajectory-bootstrapped harness evolution with audit/gate/rollback* — distinct from governance frameworks, fuzz-harness generation, and benchmark-requiring optimizers.
