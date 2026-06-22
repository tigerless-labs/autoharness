# workflow — the design spine

The governing principle, the end-to-end pipeline, and the cross-cutting invariants every
step holds. Per-step docs and [index.md](index.md) hang off this. See [`DEFINITION.md`](../DEFINITION.md)
for product intent, [`DECISION.md`](../DECISION.md) for why the SkillOpt skeleton.

## Principle

**Maintain the symbol layer; do not grow it.** The harness symbol layer (CLAUDE.md / skills /
rules / memory) is not free — it bloats, overfits, pollutes decisions, and gets ignored. The
system closes one loop from real session outcomes to **gated, human-reviewed, never-auto-written**
symbol edits, and the default verdict on any symbol is a *maintenance* action (enforce / merge /
compress / generalize / retire), not addition. Addition is the last resort, behind a recurrence
gate.

## Pipeline

```
 session records          ┌────────── read-only ──────────┐
 (~/.claude, git)  ──────► │ Observe → Detect → Attribute  │
                          └───────────────┬───────────────┘
                                          │ (episode, symbol, attribution-class, evidence)
                          ┌───────────────▼───────────────┐
                          │ Decide-action → Verify (gate)  │
                          └───────────────┬───────────────┘
                                          │ proposed symbol diff + health view
                          ┌───────────────▼───────────────┐
                          │ Stage  ──(human)──►  Adopt     │   ◄── never auto-write
                          └───────────────────────────────┘
```

- **Observe** — read-only ingest of session traces and repository/VCS state into normalized
  records. No writes, no network. Carries both channels Detect needs.
- **Detect** — isolate candidate *failure episodes* on two channels: the **objective structural
  channel** (the trace's own tool/test/build failures) as the dense, high-recall spine, and the
  **explicit user-correction channel** as a sparse high-value overlay. Correction detection
  excludes interrogatives before anything downstream.
- **Attribute** — map each episode to the responsible symbol(s) and an **attribution class**:
  *in-scope-violation* (rule present, applicable, ignored), *scope-mismatch* (rule narrower than
  the recurring correction), *gap* (no symbol), or *conflict* (a symbol actively produces the
  rejected behavior). Omission classes additionally require an **applicability** estimate.
- **Decide-action** — given (symbol, class, evidence), select from the maintenance action set
  (the value map in [maintain.md](maintain.md)). Class determines the lever: violation → enforce;
  scope-mismatch → generalize; conflict → retire/override; gap → addition only behind the
  recurrence gate.
- **Verify (gate)** — every change must verifiably net-improve on a replay/measurement set built
  from the user's own history, judged by an action-appropriate criterion, preferring objective
  zero-oracle checks. Gate strength scales with the action's reversibility and blast radius.
- **Stage → Adopt** — emit a reviewable diff plus a symbol-health view; a human adopts. Borrowed
  wholesale from the SkillOpt shell (dry-run / staging / consent).

## Invariants

1. **Never auto-write.** Human adoption is structural grounding against self-evaluation bias, not
   a convenience toggle. *why:* pure self-improvement dies of self-preference (`DEFINITION §2`).
2. **Maintain, not grow.** Addition is last-resort behind the recurrence gate; the default action
   on a symbol is maintenance. *why:* the scarce work is curation, not accumulation (`DEFINITION §3`).
3. **Objective signal is the spine; user correction is the overlay.** Detection leads with the
   structural failure channel; phrase-mining of corrections is rejected as primary, and any
   correction detector excludes interrogatives. *why:* on real data the structural channel is far
   denser and higher-precision; phrase mining is ~one-in-twenty precision on a bilingual user.
   *evidence:* [E1](../../experiments/E1_signal_density/), [E2](../../experiments/E2_attribution/).
4. **Attribution emits a class, and the class chooses the lever.** Violation→enforce,
   scope-mismatch→generalize, conflict→retire, gap→gated-add. A present-but-ignored rule is never
   answered with more text. *why:* the highest-recurrence real correction mapped to an *existing
   ignored* rule — coverage was not the problem, adherence was.
   *evidence:* [E2](../../experiments/E2_attribution/).
5. **Adherence (执行率) is a first-class measured quantity.** Whether a present, applicable symbol
   was followed is measured, not assumed. *why:* it is where the highest-value corrections land,
   and it is the moat's numerator (`DEFINITION §7`).
6. **Omission requires applicability; without it, output is a review candidate, not a verdict.**
   v1 acts only where firing/adherence is objectively observable (skill invocation, VCS-checkable
   behavior, presence/dedup/token cost); semantic applicability is a v2 estimator. *why:* raw
   adherence rates are uninterpretable without the applicable-session denominator.
   *evidence:* [E3](../../experiments/E3_applicability/).
7. **Every change passes a gate; the gate prefers zero-oracle objective checks and scales with
   risk.** Deterministic migrations (hookify) need none; deletions need adherence + flaw-rate;
   additions need a held-out flaw-rate drop. *why:* regression discipline applied to harness
   evolution is the benchmark-free quality definition (`research_results/synthesis/benchmark-free-validation.md`).
8. **Keep an exploration budget.** Reserve capacity to probe symbols the loop would otherwise
   never revisit. *why:* outcome-driven loops collapse onto familiar routines (APEX).
9. **Observe is read-only and fails safe.** Ingest never writes, never calls the network, and
   redacts secrets/PII at the boundary. *why:* an autonomously running maintainer must not be able
   to harm the records it reads (`CLAUDE.md` security).
