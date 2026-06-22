# Execution roadmap — autoharness

Program-level roadmap (spans many changes; working artifact, exempt from design-doc style rules).
Expands `DEFINITION §8` into phased, gated execution. Each phase names its goal, what ships, the
gate to advance, and the experiment evidence that de-risks it. Design is in
[`docs/design/`](../design/index.md); the WHAT/WHY lives there, this is the WHEN/ORDER.

Pinned baseline: design spine + nine invariants committed; E1–E3 measured on real `~/.claude`.

---

## Phase 0 — walking skeleton (the signature-conflict vertical slice)

**Goal.** Run the *entire* pipeline end-to-end on the one case that is fully objective, so the
architecture is exercised before any LLM or replay exists.

**Why this case.** "commit 不要有 claude 的标识" recurs across 11 sessions, is produced by an
explicit harness instruction (a *conflict*, not a slip), and its adherence is measurable by
`git log` alone — zero oracle, zero LLM. It touches every stage: detect (recurring correction) →
attribute (conflict → the instruction symbol) → decide (retire/override → hookify the user's
preference) → verify (grep before/after) → stage (reviewable diff). *evidence:* E3.

**Ships.** Observe+Detect for the correction channel (interrogative-excluded); an attributor that
resolves this conflict to its source symbol; an action proposer that emits a hookify/override
diff; a `git log` gate; a staged diff + a one-symbol health view. No auto-write.

**Gate to advance.** The slice reproduces the measured signature persistence, proposes the hook,
and the objective gate confirms the flaw rate would drop — reviewed and adopted by a human once.

## Phase 1 — v1, the $0 static maintenance slice

**Goal.** Useful maintenance with **no LLM, no replay** — only signals that are cheap and
objectively computable (`DEFINITION §8` v1).

**Ships.** Across a project's symbol layer: duplication/near-duplicate detection (dedup/merge
candidates), token/length vs presence (compress candidates), mechanically-enforceable rules
(hookify candidates), dormant skills and VCS-checkable behaviors (coarse retire / enforce
candidates). Output is a reviewable diff plus the symbol-health view; everything semantic is a
*candidate*, never a verdict (invariant 6).

**Gate to advance.** On the user's own repos, v1 surfaces real dedup/hookify/retire candidates a
human accepts, with no false "auto-fix"; the health view is legible enough to act on.

**Risk watched.** v1 must not regress into a growth/extraction tool (the ECC failure mode) — it
proposes maintenance, addition stays behind the recurrence gate.

## Phase 2 — v2, attribution + applicability + replay

**Goal.** Cross from objectively-observable to semantic — the moat.

**Ships.** (a) the LLM **applicability estimator** (per-symbol × per-session relevance) that turns
raw adherence proxies into real 执行率 and unlocks prose-rule omission; (b) trace-level attribution
(borrow HarnessFix trace-IR + GEPA reflection-credit, sunk to rule granularity); (c) replay-based
verify for behavior-no-regression on a history-built set; (d) the scope-mismatch → generalize lever.

**Gate to advance.** Attribution-to-specific-rule stays stable under the estimator (re-validate the
E2 hand result at scale); replayed edits show repairs > regressions; the applicability estimator
is calibrated against held-out adherence the user confirms.

**Open risk.** Self-preference in any judge (RHO's known weakness) — keep human adoption (invariant
1) and prefer objective gates; treat LLM judge scores as advisory.

## Phase 3 — breadth and credibility

**Goal.** Generalize and prove.

**Ships.** Source adapters beyond Claude Code (Codex, others); a SWE-bench + auto-harness
*demo* purely for credibility (not a daily judge, `DEFINITION §5`); the symbol-health dashboard as
the distribution surface; an explicit exploration budget against routine collapse (invariant 8, APEX).

---

## Cross-phase discipline

- Each phase follows the task lifecycle (`CLAUDE.md`): plan → docs → tests → code → verify → gate.
- New empirical claims are measured under `experiments/` before they enter a doc, linked as
  `evidence:`. The next measurements due: detection-precision of the interrogative filter at scale,
  and applicability-estimator calibration (both Phase 2 entry criteria) — tracked in
  [`docs/TODO.md`](../TODO.md).
- The competitive time-window (`DEFINITION §9`: ECC could add a gate) argues for shipping Phase 0–1
  visibly and early; the moat (Phase 2) is what no one else has, but it only matters if the shell
  exists to carry it.
