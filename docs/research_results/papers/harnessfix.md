# [论文] HarnessFix: From Failed Trajectories to Reliable LLM Agents — Diagnosing and Repairing Harness Flaws

**Chen, Wang et al.** — [arXiv:2606.06324](https://arxiv.org/abs/2606.06324) · 2026-06 · no public code.

Answers "**which harness layer caused the failure**", *after* something else flagged the trajectory as failed. Trajectory-level failure is **not** self-derived — it comes from the external benchmark oracle (SWE-Bench resolved / Terminal-Bench tests / GAIA exact-match / AppWorld goal completion); the diagnosis agent just reads the externally-evaluated result.

Its contribution is *step-level attribution inside a known-failed trajectory*:
- Compile raw traces + harness code into a **Harness-aware Trace IR (HTIR)** — `TraceStep` nodes (Role, Execution Status, Artifact/state effect) linked by temporal / input-provenance / control-flow edges.
- An **LLM diagnosis agent** does backward evidence-backtracking → ranked candidate responsible steps → adjudication → maps to one of **7 ETCLOVG layers** (Execution/sandbox, Tool interface, Context/memory, Lifecycle/orchestration, Observability, Verification/eval, Governance/security).
- Repair gate = **TargetImprovement** (ΔD_target ≥ δ_min, flaw occurrence *re-diagnosed* on new trajectories, no ground-truth label — the benchmark-free verify worth borrowing) **+ RegressionBound** (R_new ≤ r_max, anchored to the benchmark oracle).

**Relevance to autoharness:** borrow the step-attribution + re-diagnose-verify. The failure *definition* (benchmark oracle) does **not** transfer, and the 7-layer granularity is far coarser than the per-rule granularity autoharness needs. Caveat: only R_new is objective; ΔD_target carries the same LLM-attribution noise as the original diagnosis.
