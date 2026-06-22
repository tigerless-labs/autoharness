# MUSE-Autoskill — skill lifecycle management

**Lin, Li, Song, Jiang, Zhang** — "MUSE-Autoskill: Self-Evolving Agents via Skill Creation, Memory, Management, and Evaluation" ([arXiv:2605.27366](https://arxiv.org/abs/2605.27366), 2026-05, 30pp).

> Already noted in the cluster file ([../skill-learning-papers.md](../skill-learning-papers.md)); this is the per-paper read.

Problem: skill-creation methods treat skills as "isolated and static artifacts," limiting reuse, reliability, and long-term improvement. MUSE (Memory-Utilizing Skill Evolution) manages a unified skill lifecycle:
- **Creation** — generate skills on demand.
- **Memory** — per-skill memory accumulates experience across tasks.
- **Management** — organize and select skills efficiently.
- **Evaluation/Refinement** — validate via **unit tests and runtime feedback**.

Central reframing: skills as long-lived, experience-aware, **testable** assets.

Results: SkillsBench — preliminary evidence of gains in task success, efficiency, skill reuse, and cross-agent transfer (authors mark it work-in-progress).

**Relevance to autoharness:** the *unit-test-the-skill* idea is the validation mechanism a harness optimizer needs; the per-skill memory is the substrate trajectory-bootstrapping reads from.
