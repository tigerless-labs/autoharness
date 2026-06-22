# maintain — action, gate, and staging

Turns an attributed episode into a gated, reviewable symbol edit. Spine: [workflow.md](workflow.md).

## Value map → action

Each symbol is valued as *relevance × gain-when-followed − resident cost (tokens + attention
dilution + conflict)*. This is a map of what to measure, not a computable score (`DEFINITION §3`):
per-symbol relevance, gain, and dilution are open problems, so the stage emits **evidence-backed
action proposals, not precise rankings**. The attribution class ([attribute.md](attribute.md))
plus the value signals select an action from the maintenance set, borrowed from Bayesian-Agent and
extended:

| Symbol condition | Action |
|---|---|
| high value, mechanically enforceable | **hookify** — move to a deterministic hook |
| high value, judgement-bound | **keep** |
| overlaps a higher-value symbol | **dedup / merge** |
| narrower scope than the recurring need | **generalize** |
| long relative to its value | **compress** |
| present, applicable, ignored | **enforce** (hookify / reposition) |
| actively produces a rejected behavior | **retire / override** |
| never followed, no gain, pure conflict | **retire** |
| genuine gap, recurring | **add** — last resort, behind the recurrence gate |
| value uncertain, cheap to test | **measure** |

## The recurrence gate on addition

Addition is the one action that grows the layer, so it carries the strictest precondition
(`DEFINITION §8`): a candidate symbol is added only if the episode **recurs** across many distinct
sessions, **cannot be merged** into an existing symbol, and **passes the verify gate**. A single
occurrence never mints a rule. Recurrence is real and measurable on history — the gap themes recur
across dozens of sessions. *evidence:* [E2](../../experiments/E2_attribution/).

## Verify — the gate per action

Every change net-improves on a replay/measurement set built from the user's own history, judged by
an **action-appropriate** criterion, preferring objective zero-oracle checks; gate strength scales
with reversibility and blast radius:

- **hookify** — deterministic migration; behavior-preservation check, no judge.
- **dedup / compress / generalize / refactor** — behavior-no-regression on the replay set.
- **retire / override** — adherence and the flaw's recurrence must not worsen once removed.
- **add** — a held-out drop in the flaw's recurrence ("flaw 出现率降没降"), the benchmark-free
  verify that needs no ground-truth labels.

Where the behavior is VCS- or trace-checkable, the gate is a direct objective measurement with no
oracle and no LLM — the strongest available evidence. *evidence:* [E3](../../experiments/E3_applicability/).

## v1 / v2 boundary

- **v1** acts only where firing and adherence are **objectively observable** — skill invocation
  counts, VCS-checkable behaviors, presence, duplication, token cost. It ships dedup / compress /
  hookify / coarse-retire as a reviewable diff plus a symbol-health view; it never replays, never
  deep-attributes, and presents semantic omissions as candidates.
- **v2** adds the LLM applicability estimator, trace-level attribution, and replay-based gating,
  unlocking scope-mismatch generalization and prose-rule omission.

## Stage → Adopt

Output is a reviewable diff and a symbol-health view; a human adopts. Never auto-write (invariant 1).
The dry-run / staging / consent shell is taken wholesale from SkillOpt (`DECISION.md`).
