# attribute — episode to responsible symbol

Maps each failure episode to the symbol(s) accountable and the action-determining class.
The make-or-break stage (`DEFINITION §8` hard point 1). Spine: [workflow.md](workflow.md).

## Feasibility

Attribution of a real correction to a *specific* symbol is feasible — every sampled correction
resolved to a named existing symbol or a confident "no symbol" — **conditional on** the detection
filter ([detect.md](detect.md)). The bottleneck is mis-detection, not mis-attribution.
*evidence:* [E2](../../experiments/E2_attribution/).

## The attribution classes

Attribution is not binary; it emits one of four classes, and the class — not the episode — chooses
the downstream lever:

- **in-scope-violation** — a symbol exists, applies, and was ignored. Lever: *enforcement*
  (hookify, reposition, or compress the noise competing for attention), never more text.
- **scope-mismatch** — a symbol covers a narrower scope than the recurring correction. Lever:
  *generalize* the existing symbol, not a sibling beside it.
- **gap** — no symbol covers the episode. Lever: *addition*, and only behind the recurrence gate.
- **conflict** — a symbol actively produces the rejected behavior. Lever: *retire or override* the
  polluting symbol. This is the thesis in one case (`DEFINITION §2` 符号污染决策); its canonical
  instance is a harness instruction the user has repeatedly countermanded.

Answering a present-but-ignored rule with another rule is worthless; separating violation from gap
is therefore the stage's core discrimination. *evidence:* [E2](../../experiments/E2_attribution/).

## Applicability — the omission half

A violation or conflict is visible because the symbol or the rejected behavior is in the trace.
**Omission — a symbol that should have fired but didn't — is not in the trace**, so trace-reading
cannot find it; it is reached by matching the failed episode's intent against the symbol catalog.
That match needs an **applicability** estimate: was this symbol even relevant here? Adherence
(执行率) is meaningful only against that denominator — a low raw firing rate over all sessions is
not a violation if most sessions were out of scope.

Applicability for skills is partly observable (invocation is a trace fact); for prose rules it is
a semantic judgement. Without the estimate, an omission is a **review candidate, not a verdict** —
which is the v1/v2 boundary ([maintain.md](maintain.md)). *evidence:* [E3](../../experiments/E3_applicability/).
