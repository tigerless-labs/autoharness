# SKILL.md format spec — authoring + #416 lint, single source

Every agent-authored skill is one `SKILL.md` (plus any files it references) and must satisfy the
checks below. REF authors against this spec; the promoter's deterministic linter enforces it. Both
read this one file — keep them aligned.

## Required frontmatter

YAML frontmatter that parses, carrying at least:

- `name` — short identifier for the skill.
- `description` — one specific line; this is what the host matches on for recall, so vague
  descriptions degrade recall and are rejected.

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

## Global is stricter (repo-agnostic)

A `global`-level skill loads in every project, so its blast radius is every project. It must not
embed repo-local identifiers — absolute paths, the current repo name, or repo-specific ids. Such
content downgrades the skill to `project`, or is rejected.
