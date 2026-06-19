# autoharness

> **TODO**: one-paragraph project statement — what autoharness does, and the one-line wedge
> vs neighboring tools. Fill this in with the first design doc.

## Key docs (read before changing the relevant area)

- **[docs/design/](docs/design/index.md)** — the architecture and the *why*. Start at the spine
  (`docs/design/workflow.md`: principle + pipeline + invariants), then the step you're touching.
  *(Create these as the design solidifies; keep the index current.)*
- **[docs/TODO.md](docs/TODO.md)** — tracked follow-ups not yet on the roadmap.
  **Keep this current in real time** (see rule below).
- **[docs/testing.md](docs/testing.md)** — test conventions and the per-file test map.
- **[docs/plans/](docs/plans/)** — per-change implementation plans (working artifacts, exempt
  from the design-doc style rules).
- **[docs/solutions/](docs/solutions/)** — institutional learnings from past debugging and
  execution, read back by future planning.

## Invariants — do not break

> **TODO**: numbered, non-negotiable design invariants — added as they are discovered, never
> removed silently. Each one states the rule and the *why* in one or two sentences, with an
> `evidence:` pointer (experiment/measurement) when the rule rests on an empirical claim.

## Task lifecycle — the fixed order for every non-trivial change

Plan → sync → docs → tests → code → verify → commit → docs/index sweep → green CI.
Trivial one-line changes skip the plan; nothing skips the order. A change that arrives
out of order is *incomplete*.

1. **Plan.** Non-trivial changes start with a plan in `docs/plans/` (working artifacts,
   exempt from the design-doc style rules). The plan's first unit updates the relevant
   `docs/design/` doc; every unit places tests before code.
2. **Sync the baseline.** `git fetch`, then rebase the task branch onto the latest `main`
   before developing — always build on the current main baseline, never a stale one. Land
   work via feature branch + PR; no direct pushes to `main`.
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

## Concurrent development — parallel agents

Multiple agents develop in parallel; isolation is mandatory and the repo root is sacred.

- **One task, one branch, one worktree.** Each agent binds to exactly one explicit task, on its
  own branch, in its own worktree — **created with Claude Code's own worktree tooling** (the
  `/ce-worktree` skill or the built-in worktree feature), which places the worktree under
  `.claude/worktrees/<branch>` (`.claude/` is git-ignored). Do not hand-create worktrees with raw
  `git worktree add`. Never develop on the default/trunk branch — `main`/`master`/`trunk`, **or
  whatever the repo's current default branch is**.
- **The root checkout is for review, merge, and release only.** No agent develops or commits in
  the repository root or on the default branch.
- **Verify the branch before every commit.** Run `git branch --show-current` and confirm it
  equals your task branch before any `git commit`. On mismatch, stop and investigate — never
  commit to whatever branch happens to be checked out.
- **Declare scope before starting.** State the task goal, the modules you own, the paths you may
  modify, and the paths you must not touch.
- **No shared-surface collisions.** By default, two agents must not concurrently modify the same
  file, schema, public contract, shared config, or deploy entry.
- **Single-writer for shared surfaces.** A schema, migration, public API contract, shared
  config, deploy, or lock-file change has exactly one writing agent at a time.
- **Contract before implementation.** For cross-module changes, merge the contract first, then
  build the implementations that depend on it.
- **Report on delivery.** Each agent hands off with: scope of changes, test results,
  schema/config/deploy impact, and remaining risks.
- **Merge gate.** A branch merges only after the relevant unit tests, system tests, and
  doc-automation checks pass; changes touching a data module must additionally pass schema,
  migration, and data-monitoring tests.

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
