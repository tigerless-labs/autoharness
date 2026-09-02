# SKILL.md format spec — authoring + #416 lint, single source

Every agent-authored skill is one `SKILL.md` (plus any files it references) and must satisfy the
checks below. REF authors against this spec; the promoter's deterministic linter enforces it. Both
read this one file — keep them aligned.

## Required frontmatter

YAML frontmatter that parses, carrying at least:

- `name` — short identifier for the skill.
- `description` — the trigger; see "Description is the trigger" below. This is what the host matches
  recall on, so a cue-less label never fires and is rejected.

- `category` — one lowercase word or hyphenated phrase naming the class of work the skill serves
  (`testing`, `git-workflow`, `deployment`). An open set: **pick one already visible in the injected
  index**, and mint a new one only when nothing existing fits — the index is the candidate list, and
  a library of near-synonym categories groups no better than none. It is what the session-start index
  groups by, so a skill without one lands in `general`.

  Enforcement is deliberately asymmetric with the description gate: an illegal value (anything but a
  single safe segment of letters, digits, `.`, `_`, `-`) is **rejected**, but a *missing* one is
  **allowed through** and noted in the run account — a cue-less description can never be recalled at
  all, while a missing category only files the skill badly. The curator backfills what lands without
  one.

## Description is the trigger — one sentence, inside the index budget

The description is the routing signal, and it **is the index line**: the session-start index renders
one line per skill from it, and the host preloads it too. So it has exactly one job — make the right
task match — and one budget: `INDEX_DESC_MAX_CHARS`. Over budget, the index truncates to
`INDEX_DESC_MAX_CHARS - 3` + `...` and the routing signal dies mid-clause, so a `create`/`update`
over it is **rejected**. `patch` is exempt, so a legacy over-long description stays fixable.

Write **one sentence, trigger first, ending in a period**. Name the concrete objects and the words a
user would actually type — the nouns, verbs, tools and file types. Detail goes in the body; the
description is not a summary of the skill, it is the thing that decides whether the skill is even
read.

Good, all inside the budget:

    Use when a fetch fails: 403/429, paywall, WAF, bot wall.
    Search arXiv papers by keyword, author, category, or ID.
    4-phase root cause debugging: understand bugs before fixing.

Bad: `Manages project operations` — a topic label with no trigger at all; nothing a user types
matches it.

Bad: a 300-char paragraph opening with a verb phrase and reaching `Use when …` only halfway through.
It reads well in a file and is a fragment in the index, which is where recall actually happens.

One sentence straining to cover five distinct triggers → split into separate skills, each with its
own.

**Enforced (a floor, not the standard):** the promoter rejects a `create`/`update` whose description
exceeds `INDEX_DESC_MAX_CHARS`, or carries no trigger cue at all — neither a `when` clause nor a
quoted phrase. Passing is not the same as routing well; that judgment stays the author's.

## Structure (#416)

- Frontmatter parses as YAML; `name` and `description` are present and non-empty.
- Every file referenced by a relative path in the body exists.
- Every referenced `.py` file parses (no syntax error).
- No broken symlinks.

## Subfiles (folder-skill)

A skill is a folder: `SKILL.md` plus optional subfiles, carried in the same intent (`files`:
relative path → content, `create`/`update` only). Four whitelisted top-level directories, each
with a distinct meaning — put content where it belongs:

- `references/` — session-specific detail and condensed knowledge banks (quoted research, API-doc
  excerpts, domain notes). Concise and task-focused, not a mirror of upstream docs.
- `templates/` — starter files meant to be copied and modified (boilerplate, scaffolding, a
  known-good example).
- `scripts/` — re-runnable actions the skill invokes directly (verification scripts, fixture
  generators, probes) instead of retyping them each run.
- `assets/` — static support files.

Path rules (deny-by-default, violations reject the intent):

- Relative only, at least two `/`-separated segments, the first from the whitelist above.
- Every segment matches `[A-Za-z0-9][A-Za-z0-9._-]*` — no `..`, no dotfiles, no absolute paths,
  no empty segments, no backslashes.

Pointer rule: every subfile carried in the intent must be referenced by its relative path
somewhere in the `SKILL.md` body — an unpointed subfile is invisible to future readers and is
rejected. Conversely, a whitelisted-directory path referenced in the body must be carried in the
same intent or already live in the skill folder.

`references/evidence-*.md` files are promoter-materialized provenance (the ledger points at
them); they are never authored in an intent and are exempt from the pointer rule. Intents can
neither carry them in `files` nor target them with `remove_file`.

A subfile that is no longer needed is dropped with the `remove_file` action (one relative path
per intent, same path rules). The live `SKILL.md` must no longer reference the path — patch the
pointer out first; both intents can ride the same run, they land in order.

## Content completeness

- No `TODO`, no placeholder tokens (`FIXME`, `XXX`, `<...>`), no empty sections.

## Altitude — the body is a rule, not a transcript

A SKILL.md exists to hand the next session a *durable rule*, stated at the altitude of the class of
work — not to replay the episode that produced it. So:

- **Open with the rule itself.** The first content after the frontmatter is the reusable directive in
  one or two lines. A reader who stops there already has the skill.
- **A full explainer is a smell.** A body carrying the whole Pattern / Example / When-to-use /
  Anti-patterns quartet inline is documentation, not a rule — hoist the bulk into `references/` and
  leave a one-line pointer. The SKILL.md stays the rule; `references/` holds the backing detail.
- **Hard cap (enforced):** the body (frontmatter excluded) must be at most `SKILL_BODY_MAX_LINES`
  non-blank lines — the promoter rejects a `create`/`update` over the cap. The cap is a crude proxy
  for altitude; the real judgment ("is this a rule or a retelling?") is the author's. `patch` is
  exempt, so an existing over-long skill can still be amended and trimmed.

## Global is stricter (repo-agnostic)

A `global`-level skill loads in every project, so its blast radius is every project. It must not
embed repo-local identifiers — absolute paths, the current repo name, or repo-specific ids. Such
content downgrades the skill to `project`, or is rejected.
