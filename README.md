<h1 align="center">autoharness</h1>

<p align="center">
  <img src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Ftigerless-labs%2Fautoharness%2Fmain%2F.claude-plugin%2Fplugin.json&query=%24.version&label=release&prefix=v&color=brightgreen" alt="release" />
  <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg" alt="python" />
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS-lightgrey.svg" alt="platform" />
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="license MIT" />
</p>

**autoharness is a self-learning skill layer for Claude Code.** It **learns** skills from your real
sessions, **merges** same-scenario ones instead of stacking near-duplicates, **updates** them in use,
and **prunes** any that stop getting used — so the layer **stays clean on its own**, **touching only
the skills it wrote itself**.

Same model, different harness — 42% → 78% on CORE-Bench ([HAL](https://arxiv.org/abs/2510.11977)).
The harness does much of the work (swyx's **Big Model vs Big Harness**), yet it's still rebuilt by
hand every model generation. autoharness bets one slice of it — the skill layer — can maintain itself.

| | |
|---|---|
| **Learns from real work** | Each episode is distilled into a skill from the session you were already having — no separate data-collection or replay loop. |
| **Groups, doesn't just pile up** | A new episode doesn't always add a skill — the reflector compares it against what's there and folds same-scenario skills into one, so the layer consolidates by category instead of accreting near-duplicates. |
| **Validated in use, not on a benchmark** | A skill survives by being adhered to in later turns (usage rate), not a held-out score. No oracle on the active path, and no tokens spent on a dedicated eval. |
| **Only its own skills** | Touches only the skills it generated through this plugin — everything else, whether you wrote it or installed it, is left completely alone. |
| **Evidence kept for later** | Every create/update logs its scenario and decision to a per-skill ledger — the raw material to build a benchmark from real usage if you ever want one. |

## Install

**Requires `python3` on your PATH** — autoharness runs entirely as Python (zero third-party
dependencies); its hooks and MCP server won't fire without it.

Type these in the Claude Code input box.

```
/plugin marketplace add tigerless-labs/autoharness
/plugin install autoharness@autoharness
```

Then run `/reload-plugins` (or restart Claude Code).

Zero config. It now watches your sessions and lands learned skills into `.claude/skills/` in the
background. Cadence and lifecycle thresholds are tunable — see [Configuration](#configuration).

### Update

```
/plugin marketplace update autoharness              # pull the latest release
/plugin update autoharness                          # update the installed copy
/reload-plugins                                     # apply in the running session
```

`/reload-plugins` re-arms the hooks and the MCP server in place; restarting Claude Code works too.
The installed copy is cached by the version in `plugin.json`; releases always bump it, which is
what makes the update take effect.

### Uninstall

```
claude plugin uninstall autoharness@autoharness     # stops the hooks + MCP server
claude plugin marketplace remove autoharness        # optional — also drops the install source
```

Uninstalling only stops it from running — the skills it landed and its own state live **outside** the
plugin and stay on disk. To clear those too, delete its state dir (`~/.claude/autoharness/` global,
`<repo>/.claude/autoharness/` per project) and the self-authored skills under `.claude/skills/` (each
carries a `self-authored` ledger marker, so they're easy to tell from yours). Your own skills are
never touched.

## Configuration

Every knob is an `AUTOHARNESS_*` environment variable with a built-in default — nothing to
configure unless you want to change the pace.

| Variable | Default | What it does |
|---|---|---|
| `AUTOHARNESS_REFLECT_EVERY_N` | `10` | Reflection cadence: a background reflection run fires every N host turns, and each run receives that full N-turn window. Lower = learns faster, spawns more child sessions. |
| `AUTOHARNESS_DIGEST_EXCHANGES` | `20` | How many exchanges *before* the episode window are compressed into the reflector's prior-context digest (text + tool names only). |
| `AUTOHARNESS_MATURITY_PROJECT` | `100` | Probation gate, project layer: after this many requests have arrived in its layer since a skill landed, it faces graduation review — never used across the whole probation → archived; used at least once → graduates into the mature pool. Until then it's recalled as usual but can't be archived. |
| `AUTOHARNESS_MATURITY_GLOBAL` | `300` | Same gate for the global layer — higher because a global skill loads in every project. |
| `AUTOHARNESS_CAPACITY_PROJECT` | `50` | Cap on *mature* skills in the project layer. For graduates, capacity contention is the only death: nothing is archived until the mature pool exceeds this, then the lowest usage rates go first. |
| `AUTOHARNESS_CAPACITY_GLOBAL` | `20` | Same cap for the global layer — smaller because its blast radius is every project. |

Set them in the environment Claude Code launches with — either the shell
(`export AUTOHARNESS_REFLECT_EVERY_N=3`) or the `env` map in `.claude/settings.json`:

```json
{ "env": { "AUTOHARNESS_REFLECT_EVERY_N": "3" } }
```

Hooks read the environment on every event, so a change applies from the next session. The defaults
are deliberate placeholders pending empirical calibration (tracked under `experiments/`); size caps
on captured windows and staged skill bodies are fixed constants, not env knobs.

## How it works

A learning pipeline runs beside the host and stays off its recall path — symbols are plain native
skills, recalled by the host's own name-and-description mechanism as if a human had written them.

<p align="center"><img src="docs/assets/pipeline.svg" alt="autoharness pipeline: host → CAP → REF → promoter → .claude/skills → host, with MNG and LED beside" width="760" /></p>

<sub>Diagram source: [`docs/assets/pipeline.mmd`](docs/assets/pipeline.mmd) — re-render to `pipeline.svg` after editing.</sub>

| Component | Role |
|---|---|
| **CAP** · capture | Hook-driven dumb pipe: grabs each turn (user input, agent output, tool I/O), redacts at egress, points back at the host log instead of copying it. |
| **REF** · reflect | At an episode boundary, receives the current episode window in full detail (the last N turns, tool I/O included) plus a compressed digest of the exchanges before it (text and tool names only), reads the existing skill index, and decides add / merge / patch / drop a support file / delete — emits an intent (body, delta, or path, plus reason and evidence). Proposes only; no write tools. |
| **promoter** · validate·store | The only writer. Lints the intent in memory (safety, structure, ledger, completeness, self-authored-only) and on pass does an atomic rename into the live skill directory. |
| **MNG** · lifecycle | Daemon-free: recomputed lazily at session start, once per session. Ranks symbols by usage rate — uses over the requests that arrived since the symbol was created, so the measure is opportunity-relative and a closed laptop doesn't age anyone out (the wall-clock replacement). A use is counted whenever the host consumes the skill: a Skill-tool invocation or a read of any file in the skill's directory (measured to be the dominant path). New symbols sit in probation until they've had a fair sample of requests: recalled as usual, but neither counted against the cap nor evictable. At maturity, graduation review: zero use across the whole probation → archived, never enters the pool. For graduates, capacity contention is the only death — nothing is archived until a layer's mature pool exceeds its cap, then the lowest rates go first. Archives, never deletes: an archived symbol is a directory moved out of recall, and moving it back revives it. |
| **LED** · ledger | Per-symbol append-only sidecar: why each symbol was born or changed, with evidence and a reflection watermark. Kept out of the skill body so recall stays clean. |

## Walkthrough: watching it learn

Everything autoharness does lands on disk as plain files — a demo is just opening them in the
right order. For a fast-paced run, speed up the loop first (see [Configuration](#configuration)):

```json
{ "env": { "AUTOHARNESS_REFLECT_EVERY_N": "1",
           "AUTOHARNESS_MATURITY_PROJECT": "5",
           "AUTOHARNESS_CAPACITY_PROJECT": "2" } }
```

**1 · The pipeline running.** Work a few normal turns on anything non-trivial (debug something,
figure out a workflow). Every Nth turn a background reflection fires — nothing blocks your session.
Its bookkeeping is visible in the state dir:

```
ls .claude/autoharness/        # per project — ~/.claude/autoharness/ for the global layer
  requests                     # layer request counter (MNG's denominator)
  session-<id>                 # per-session turn count toward the next reflection
  offset-<id>                  # byte watermark: where the last captured window ended
  intents/                     # queued skill proposals awaiting the promoter
```

**2 · A skill is born.** After a reflection lands, a new folder appears under `.claude/skills/`
(project) or `~/.claude/skills/` (global — for techniques that aren't repo-specific). Use `ls -la`:
the interesting files are hidden.

```
.claude/skills/<name>/
  SKILL.md                     # the skill itself — plain native format, nothing proprietary
  .ledger.jsonl                # LED: why it was born / changed (append-only)
  .sidecar.json                # lifecycle counters MNG reads
  references/evidence-*.md     # the transcript slice that justified each ledger entry
  scripts/ templates/ ...      # optional support files the reflector attached
```

**3 · LED — the paper trail.** `cat .ledger.jsonl` — one JSON line per lifecycle event:

```json
{"action": "create", "reason": "User asked about the correct command to update a plugin ...", "evidence": "references/evidence-21cd22cc.md"}
{"action": "patch",  "reason": "User discovered /reload-plugins is required in-session ...",  "evidence": "references/evidence-1a4ec51d.md"}
```

`action` + `reason` + `evidence` — and the evidence file is a real, redacted slice of the session
that taught it, materialized by the promoter (content-addressed, so the model never names files).
This is the "evidence kept for later" from the table above.

**4 · An update, not a duplicate.** Hit the same scenario again with a correction ("that's missing
a step") and let the next reflection run. The skill layer does **not** grow a near-duplicate:
the existing skill's `SKILL.md` changes and its ledger appends a `patch`/`update` line — the
two-line ledger above is a real example. `git diff` on a project-layer skill shows the edit.

**5 · Recall is the host's, untouched.** Landed skills load like hand-written ones — same
name-and-description recall, no autoharness code on that path. When one is used — invoked as a
skill or read from its directory — `calls` in its `.sidecar.json` ticks up: that adherence count
is the validation signal.

**6 · Retirement is an archive, not a delete.** Two paths out, both a folder move to
`.claude/skills/.archive/<name>/` — ledger, evidence and all, out of recall. A skill never used
across its whole probation is archived at graduation review; after graduation, once a layer's
mature pool exceeds capacity the lowest-usage-rate skills go. Moving the folder back revives it,
history intact. With the shrunk knobs above this fires within one session; at defaults it takes
hundreds of turns.

**7 · Yours are never touched.** Every autoharness-authored skill carries the ledger marker;
anything without it — skills you wrote or installed — is invisible to the promoter and MNG.

## How it compares

A self-learning skill layer can be validated against a held-out benchmark, or against its own use.
autoharness takes the second — cheaper, and it works on a live host doing open-ended work where no
benchmark exists.

| | Grow unbounded | Offline-gated self-edit<br/>([Self-Harness](https://arxiv.org/abs/2606.09498)) | Timer + daemon<br/>([hermes-agent](https://github.com/NousResearch/hermes-agent)) | autoharness |
| --- | --- | --- | --- | --- |
| Bounds the skill layer | No | Yes | Yes | Yes |
| Validation signal | None | Held-out benchmark score | Wall-clock inactivity | Adherence in use |
| Needs a benchmark / oracle | No | Yes | No | No |
| Needs a resident daemon | No | No | Yes | No |

## Acknowledgements

[NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) — studying its
auto-skill-creation and memory-consolidation design helped sharpen autoharness's adherence-based,
daemon-free take.

Built by Tigerless Labs.

## License

[MIT](LICENSE)
