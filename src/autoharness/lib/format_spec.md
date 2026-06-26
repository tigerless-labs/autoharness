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

## Content completeness

- No `TODO`, no placeholder tokens (`FIXME`, `XXX`, `<...>`), no empty sections.

## Global is stricter (repo-agnostic)

A `global`-level skill loads in every project, so its blast radius is every project. It must not
embed repo-local identifiers — absolute paths, the current repo name, or repo-specific ids. Such
content downgrades the skill to `project`, or is rejected.
