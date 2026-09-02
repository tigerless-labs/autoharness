# SKILL.md format spec — authoring + #416 lint, single source

Every agent-authored skill is one `SKILL.md` (plus any files it references) and must satisfy the
checks below. REF authors against this spec; the promoter's deterministic linter enforces it. Both
read this one file — keep them aligned.

## Required frontmatter

YAML frontmatter that parses, carrying at least:

- `name` — short identifier for the skill.
- `description` — the trigger; see "Description is the trigger" below. This is what the host matches
  recall on, so a cue-less label never fires and is rejected.

Optional, and worth setting:

- `category` — one lowercase word or hyphenated phrase naming the class of work the skill serves
  (`testing`, `git-workflow`, `deployment`). An open set: reuse a category already present in the
  index rather than minting a near-synonym. It groups the injected recall index — omitted, the skill
  lands in `general`, and a library where everything is `general` is a flat list again. A single safe
  segment (letters, digits, `.`, `_`, `-`); anything else is rejected.

## Description is the trigger — write it to this shape

The host preloads every skill's `name` + `description` and picks among all of them by matching the
user's request against the description. The description carries the whole selection signal; a body
only matters after it has already fired. It is read twice over: in full by the host's own recall, and
truncated to `INDEX_DESC_MAX_CHARS` in the injected index. **The trigger cue must fall inside that
truncated prefix** — a `when` clause or a quoted phrase within the first `INDEX_DESC_MAX_CHARS`
characters — or the promoter rejects the `create`/`update`: past the cut the description is half a
sentence on the very recall surface this system builds. Lead with the cue, then the detail.
(`patch` is exempt, so an existing description can still be repaired.) Write it to this shape:

    <verb phrase: what it does>. Use when <the situation>, or when the user mentions <the words
    they would type, every alias for the same thing>.

Four elements, all required:

1. **What it does** — a third person verb phrase naming concrete actions and objects. The
   description is injected into the host's system prompt, so a first- or second-person phrasing
   ("I can help you…", "You can use this to…") reads as a different speaker and breaks recall.
2. **When to use it** — the situation that should fire it (`use when …`), stated in the user's
   frame, not the author's.
3. **User-facing vocabulary** — the words the user would type: the nouns, verbs, file types and
   extensions they would actually say, every alias listed. A term absent here can never be matched.
4. **Nothing else** — no imperative step, no procedure, no file path standing in for a phrase; that
   is body content. Stay under `SKILL_DESC_MAX_CHARS`, past which the host truncates.

Good: `Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help
writing commit messages or reviewing staged changes.`

Bad: `Manages project operations` — a topic label, no trigger at all.

Bad: `Use when verifying a release PR has version bumps. Check that "a.json" and "b.json" match.` —
no what-clause, an imperative lifted from the body, and the quoted strings are file paths rather than
anything a user would type.

One description straining to cover five distinct triggers → split into separate skills, each with
its own.

**Enforced (a floor, not the standard):** the promoter rejects a `create`/`update` whose description
carries no trigger cue — neither a `when` clause nor a quoted phrase — whose cue falls past
`INDEX_DESC_MAX_CHARS`, or which exceeds `SKILL_DESC_MAX_CHARS`. That check is a crude proxy; passing it is not the same as satisfying the
four elements, and the judgment stays the author's.

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
