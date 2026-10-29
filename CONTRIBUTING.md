# Contributing to autoharness

Thanks for taking a look. autoharness is a single plugin, and most of it is one pipeline:
a hook captures a turn, a reflector proposes a skill, a promoter writes it, and the
lifecycle pass eventually archives what nobody loads. If you want to change one of those
steps, read that step's module and its test first — the comments there explain the
constraints better than any summary would.

Bug reports are welcome too, but a report that comes with a failing test gets fixed much
faster than one that doesn't.

## Requirements

- **Python 3.11 or newer**, available as `python3` on your `PATH`. The hooks resolve that
  bare name, so an older interpreter earlier on your `PATH` turns every hook off for the
  session.
- **Linux or macOS.** CI runs on `ubuntu-latest` and the README advertises those two
  platforms; the suite is not green on Windows.
- **No runtime dependencies.** autoharness is standard library only, and it should stay
  that way — a dependency here runs inside someone else's session on every hook event.
  `pytest` and `ruff` are dev-only and aren't declared anywhere, so install them yourself.

## Local setup

```sh
git clone https://github.com/tigerless-labs/autoharness
cd autoharness
python3 --version                  # must be 3.11+
python3 -m pip install pytest ruff
```

Then the two commands CI runs:

```sh
python3 -m pytest -m "not live" -q
ruff check .
```

The offline run needs no model account, no API key and no Claude Code install — the tests
build their state in temporary directories and never touch your real `~/.claude`. The
`live` marker is for the few tests that drive an actual host through `tests/test_e2e_live.py`;
it is excluded everywhere, because a live host can't run in CI. If you add a test that
needs one, mark it `@pytest.mark.live` so it stays out of the offline run.

`pytest.ini` puts `src` on the path for you (`pythonpath = src`), so there is nothing to
install before importing `autoharness`. `ruff.toml` selects pyflakes, import sorting,
pyupgrade, bugbear and the key pycodestyle rules — line length is deliberately not
enforced.

## Repository layout

| Path | What lives there |
|---|---|
| `src/autoharness/hook/` | The entry points the host calls on each event: `on_session_start.py`, `on_stop.py`, `on_session_end.py`, `on_skill_call.py`, plus `capture.py`, `dispatch.py`, `promoter.py` and `spawn.py`. This is where a turn is read and a reflection is triggered. |
| `src/autoharness/lib/` | The machinery those hooks share: `validate.py` lints a proposal, `skill_store.py` and `atomic.py` are the only writers of a skill directory, `lifecycle.py` ranks usage and handles probation and archiving, `redact.py` with `redaction_rules.toml` decides what leaves the session, `layer.py` resolves which layer a write belongs to. |
| `src/autoharness/config.py` | Every `AUTOHARNESS_*` knob, its default, and the validation that rejects a bad value instead of silently applying it. |
| `src/autoharness/stage_skill/` | The MCP server the reflector calls to stage a proposal. |
| `agents/` | The reflector and curator prompts — plain markdown, but they are where the judgment about merge/patch/drop actually lives. |
| `skills/learn/SKILL.md` | The `/learn` entry point. |
| `hooks/hooks.json` | Which hook runs on which host event. |
| `docs/` | ADRs in `docs/adr/` for decisions that outlive a PR, the pipeline diagram in `docs/assets/`, the demo script. |
| `tests/` | One file per module: `lib/x.py` is covered by `tests/test_x.py`. |
| `tools/check_doc_links.py` | Dangling markdown link checker. `python3 tools/check_doc_links.py docs` checks the docs tree, `--selftest` checks the checker. |

## Where to start

- **Docs.** `docs/` is thin: one ADR, no page explaining what a skill file has to look
  like. An ADR for a decision already visible in the code, a paragraph on why a knob
  defaults where it does, or a worked example under `docs/` is genuinely useful and can't
  break the plugin.
- **Tests.** Every module under `lib/` has a matching file under `tests/`, but coverage
  inside a module is uneven. A behavior with no test is a good first change — write the
  test that pins the current behavior first, then see whether the behavior is right.
- **Small fixes.** Redaction rules, frontmatter validation and the counters are all
  self-contained, and each has tests that show the expected shape of a new case.
- **Not a good first change.** The capture window and the reflector prompts: both are
  tuned against real sessions, and a plausible-looking edit there can't be validated by
  the suite.

## First-PR checklist

- [ ] One concern per PR. A fix and an unrelated rename in the same branch is the usual
  reason a review stalls.
- [ ] If you changed behavior, add the test that fails without your change, and say in the
  PR which test that is.
- [ ] Run both commands above and say what they reported. A PR that says "tests pass"
  without output is hard to review; paste the summary line.
- [ ] If you touch `redact.py` or `redaction_rules.toml`, add a case with the secret shape
  you are covering. `tests/test_redact.py` is where every rule ends up.
- [ ] If you add or rename an env knob, update the tables in the README's Configuration
  section in the same PR — that table is the only place a user finds it.
- [ ] If you edit markdown, run `python3 tools/check_doc_links.py docs`.
- [ ] Commit messages follow the prefix already used in the history: `fix(scope): ...` for a
  fix, `test: ...` for tests only, `docs: ...` for documentation only. Lowercase after the
  prefix, no trailing period.
- [ ] The PR description says what was broken, what you changed and how you checked it.
  Link the issue if there is one.

No CLA, no sign-off requirement, and no maintainer approval needed to open a PR — just
keep it small enough to review in one sitting.
