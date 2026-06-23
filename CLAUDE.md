# autoharness

> **TODO**: one-paragraph project statement — what autoharness does, and the one-line wedge
> vs neighboring tools. Fill this in with the first design doc.

## Key docs (read before changing the relevant area)

- **[docs/](docs/index.md)** — documentation map; single entry point for the whole `docs/` tree.
- **[docs/design/](docs/design/index.md)** — the architecture and the *why*. Start at the spine
  (`docs/design/workflow.md`: principle + pipeline + invariants), then the step you're touching.
  *(Create these as the design solidifies; keep the index current.)*
- **[docs/TODO.md](docs/TODO.md)** — tracked follow-ups not yet on the roadmap.
  **Keep this current in real time** (see rule below).
- **[docs/testing.md](docs/testing.md)** — test conventions and the per-file test map.
- **[docs/plans/](docs/plans/)** — per-change implementation plans (working artifacts, exempt from the design-doc style rules).


## Invariants — do not break

Non-negotiable, added as discovered, never removed silently. The authoritative statements (rule +
*why* + `evidence:`) live in [`docs/design/workflow.md`](docs/design/workflow.md); this is the
index. Grounded in [`experiments/`](experiments/) E1–E3.

1. **Never auto-write** — human adoption is structural grounding, not a toggle.
2. **Maintain, not grow** — addition is last-resort behind the recurrence gate; default is maintenance.
3. **Objective signal is the spine, user correction the overlay** — detection leads with structural
   failure; phrase mining is rejected as primary; correction detection excludes interrogatives.
   *evidence:* E1, E2.
4. **Attribution emits a class that chooses the lever** — violation→enforce, scope-mismatch→
   generalize, conflict→retire, gap→gated-add; a present-but-ignored rule is never answered with
   more text. *evidence:* E2.
5. **Adherence (执行率) is measured, not assumed.** *evidence:* E2.
6. **Omission needs applicability; without it, output is a candidate, not a verdict** — v1 acts only
   on objectively-observable behavior. *evidence:* E3.
7. **Every change passes a gate; prefer zero-oracle objective checks; gate scales with risk.**
8. **Keep an exploration budget** against routine collapse.
9. **Observe is read-only and fails safe.**

## Task lifecycle — the fixed order for every non-trivial change

Plan → sync → docs → tests → code → verify → commit → docs/index sweep → green CI.
Trivial one-line changes skip the plan; nothing skips the order. A change that arrives
out of order is *incomplete*.

1. **Plan.** Non-trivial changes start with a plan in `docs/plans/` (working artifacts,
   exempt from the design-doc style rules). The plan's first unit updates the relevant
   `docs/design/` doc; every unit places tests before code.
2. **Branch, isolate, sync.** Bind each change to exactly one explicit task on its own branch,
   developed in its own worktree — **created with Claude Code's own worktree tooling** (the
   `/ce-worktree` skill or the built-in worktree feature), which places it under
   `.claude/worktrees/<branch>` (`.claude/` is git-ignored); never hand-create one with raw
   `git worktree add`, and never develop on the default/trunk branch (`main`/`master`/`trunk`,
   or whatever the repo's current default branch is). Before developing, `git fetch` and rebase
   that branch onto the latest `main` so you build on the current baseline, never a stale one.
   Land the work via feature branch + PR; no direct pushes to `main`.
3. **Docs first.** Read, then update, the relevant `docs/design/` doc(s) before any test or
   code — pin down behavior boundaries, interface contracts, and acceptance criteria. Never
   touch code first.
4. **Tests next (TDD).** Write the failing unit test(s) first, then the system test(s), then
   the implementation. Put each in the matching `tests/test_<module>.py`, use fixtures rather
   than live external services, and assert **relationships/invariants** (sums reconcile,
   A > B, value `> 0`) — never hardcoded values that break when an upstream dependency
   changes. A feature shipped without a test is *incomplete*.
5. **Code.** Write the code that makes the tests pass.
6. **Verify end-to-end.** Run the app on a local server and confirm the behavior end-to-end
   against a running instance — not just via unit tests.
7. **Commit.** Run the relevant unit *and* system tests before each commit; commit at every
   green-test point (the natural TDD commit moments) and `git push` after every completed task
   and at every phase gate — progress must never exist only on this machine.
8. **Sweep docs & indexes.** Confirm whether the change needs updates to the design docs and
   the doc/file-tree indexes (`docs/design/index.md`) — update them in the same change.
9. **Drive CI green.** After opening the PR, watch CI and code-quality checks (CI runs, lint,
   static analysis, doc-automation checks). On any failure, locate, fix, and push immediately
   — repeat until every required check passes.

## Working rules

- **Docs are top-level design only.** Describe *what* a piece does and *why* — never how. No
  pseudocode, no code snippets, no concrete data, values, or magic numbers. Name **modules and
  objects** — never functions, constants, ratios, or file paths; that detail lives in the code.
  Two carve-outs: **architecture diagrams** are legitimate top-level design and stay; and the
  **setup runbooks** (install, quickstart, ops) keep the literal commands a user runs, since
  the command *is* the deliverable there — but their prose still obeys the no-implementation
  rule.
- **Design docs are ruthlessly concise — every sentence earns its place.** No filler, no
  hedging, no motivational preamble, no restating what the code, a diagram, or another doc
  already says. One fact lives in exactly one place; cross-link instead of repeating. If a
  sentence adds no distinct design fact, cut it. When you edit a doc, leave it shorter than
  you found it unless you added a genuinely new idea.
- **Clear code, no comments.** Code must read clearly on its own — prefer explicit, unambiguous
  names with underscores, and carry intent through structure, naming, tests, and docs. Write no
  comments; if one feels necessary, rename or split until it isn't.
- **Decouple — one functional block, one object, one file. Never duplicate.** Every functional
  block is its own object in its own file. Never write the same functionality twice (DRY) —
  extract the shared piece and reuse it.
- **One authoritative source per fact.** A concept or piece of logic has exactly one home:
  **docs** carry intent, boundaries, constraints, and the reasons for decisions; **code** is the
  sole authority for implementation; **data** lives in the data layer and is the sole authority
  for facts. Never let the same thing live in two of them — cross-reference instead.
- **Config holds every knob.** Tunable parameters, environment differences, and policy/feature
  switches live in config — never hardcoded or scattered across the code.
- **Real-time TODO**: when you discover a follow-up, a gap, or defer something, write it into
  `docs/TODO.md` immediately (don't leave it only in chat). When you finish a TODO,
  remove or check it off. Roadmap-level items go in the design docs; smaller/uncommitted ones
  in `docs/TODO.md`.
- **Verify empirical claims by experiment before asserting** — measurements live under
  `experiments/`, and the invariant or doc that rests on them links back as `evidence:`.

## Security — agents run autonomously, so the system must fail safe

- **Trust nothing by default.** Treat external input, upstream responses, and agent decisions as
  hostile. The **core layer** especially validates input, checks bounds, rejects illegal state,
  and fails safe on error (fail-safe, deny by default).
- **Least privilege.** Default to least privilege and deny by default. Secrets and raw PII never
  enter the repo, ordinary logs, or ordinary traces.
- **Guardrails at every chokepoint.** Place guardrails at agent input/output, tool/skill calls,
  cross-module calls, external communication, destructive actions, and permission decisions — so
  an autonomously running agent cannot harm the system, the data, or users. High-risk paths must
  be able to allow / deny / redact / degrade / escalate / hand to human review.
- **Red-team the tests.** Both unit and system tests carry adversarial cases — privilege
  escalation, injection, guardrail bypass, cross-tenant leakage, dangerous tool calls, and
  failure injection — proving the system fails safe under malicious or abnormal input.
