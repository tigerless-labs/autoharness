# SKILL.md format spec — authoring + #416 lint, single source

Every agent-authored skill is one `SKILL.md` (plus any files it references) and must satisfy the
checks below. REF authors against this spec; the promoter's deterministic linter enforces it. Both
read this one file — keep them aligned.

## Required frontmatter

YAML frontmatter that parses, carrying at least:

- `name` — short identifier for the skill.
- `description` — the trigger; see "Description is the trigger" below. This is what the host matches
  recall on, so a cue-less label never fires and is rejected.

## Description is the trigger — spend the effort here

The host preloads every skill's `name` + `description` and decides recall by matching the user's
request against the description. So the description, not the body, decides whether the skill ever
fires — spend the writing effort here. A body only matters after the description has already fired.

- **Name when to use it.** State the trigger: `use when …` plus the conditions/symptoms that should
  fire it. An abstract topic-label ("Manages project operations", "Setup docs for agents") matches no
  concrete request and never fires.
- **List literal phrases the user would type.** Quote them (`"audit this"`, `"set up the project"`).
  Concrete phrases match concrete requests; abstract summaries do not.
- **One skill that wants to do five things → split into modes**, each with its own trigger phrases; a
  bloated description covers too much and matches inconsistently.
- **Enforced:** the promoter rejects a `create`/`update` whose description carries no trigger cue
  (neither a `when` clause nor a quoted phrase), or exceeds `SKILL_DESC_MAX_CHARS`. The cue check is a
  crude proxy; the real judgment (does this match how a user actually asks?) is the author's.

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
