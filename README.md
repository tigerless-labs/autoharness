<h1 align="center">autoharness</h1>

<p align="center"><strong>A per-symbol maintenance optimizer for an agent's skill layer — it learns skills from real runs and lets them earn their keep by being adhered to in use, not by an offline eval score.</strong></p>

<p align="center">
  <img src="https://img.shields.io/badge/status-built%20%26%20e2e--validated-brightgreen.svg" alt="status" />
  <img src="https://img.shields.io/badge/lifecycle-zero--daemon-blue.svg" alt="zero daemon" />
  <img src="https://img.shields.io/badge/form-Claude%20Code%20plugin-brightgreen.svg" alt="plugin" />
  <img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="license MIT" />
</p>

Agents accumulate skills, and the skill layer needs maintaining. Most approaches either grow it
unbounded or age skills out on a wall-clock timer behind a resident daemon — punishing a skill for
sitting unused even when the host never had a chance to use it.

autoharness watches a host agent's own sessions, distills each episode into a skill, and lands it
into the native skill directory (`.claude/skills`) where the host recalls it normally. Skills that
keep getting invoked survive; ones that go unused or get contradicted are archived. It runs
**beside** the host — never touching the skill load or recall path, only observing through hooks and
writing to disk. There is **no daemon**: the lifecycle recomputes lazily at session start, and
symbols are judged by **invocation rate**, not elapsed time.

> [!NOTE]
> **Built and validated end-to-end.** The full pipeline (Phases 1–7) is implemented, and the
> packaged plugin has been run on a real Claude Code host in an isolated sandbox — install →
> capture → reflect → land → invoke → archive → restore, with skills judged by invocation rate.

## Install

**Requires `python3` on your PATH** — autoharness runs entirely as Python (zero third-party
dependencies); its hooks and MCP server won't fire without it.

```
/plugin marketplace add tigerless-labs/autoharness
/plugin install autoharness@autoharness
```

Restart Claude Code, then verify it's live:

```
/plugin    # autoharness@autoharness — enabled
/mcp       # stage_skill — connected
```

That's it — zero config. autoharness now watches your sessions; at an episode boundary it reflects
in the background and lands learned skills into `.claude/skills/`, recalled by the host's own
name-and-description mechanism (autoharness never touches the recall path). Cadence and lifecycle
thresholds are tunable via `AUTOHARNESS_*` environment variables.

## How it works

A learning pipeline runs beside the host and keeps all of itself off the host's recall path.

<p align="center"><img src="docs/assets/pipeline.svg" alt="autoharness pipeline: host → CAP → REF → promoter → .claude/skills → host, with MNG and LED beside" width="760" /></p>

<sub>Diagram source: [`docs/assets/pipeline.mmd`](docs/assets/pipeline.mmd) — re-render to `pipeline.svg` after editing.</sub>

- **Author and validator are separate.** REF only proposes an intent; it has no write tools. The
  promoter is the sole writer and gates every intent through a deterministic linter.
- **Nothing lands until it passes.** The promoter shapes and lints the intent in memory and only
  then does an atomic rename into the live skill directory — no half-written skills on disk.
- **The host is never modified.** Symbols are plain native skills; the host recalls them by its own
  name-and-description mechanism, exactly as if a human had written them.

| Component | Role |
|---|---|
| **CAP** · capture | Hook-driven dumb pipe: grabs each turn (user input, agent output, tool I/O), redacts at egress, points back at the host log instead of copying it. |
| **REF** · reflect | At an episode boundary, compare-first: reads the existing skill index, decides add / merge / patch / delete, and emits an intent (body or delta, plus reason and evidence). Proposes only. |
| **promoter** · validate·store | The only writer. Shapes the intent in memory, runs a deterministic linter (safety, structure, ledger, completeness, self-authored-only), and on pass does an atomic rename into the live skill directory. |
| **MNG** · lifecycle | Deterministic and daemon-free. Ranks symbols by invocation rate per layer, shields new ones during probation, archives the weakest when a mature pool is over capacity. Archives, never deletes. |
| **LED** · ledger | Per-symbol append-only sidecar recording why each symbol was born or changed, with evidence and a reflection watermark. Kept out of the skill body so recall stays clean. |

## Design

### Adherence over eval

A skill earns survival by being followed and working across later interactions, not by a one-shot
offline score. There is no oracle and no held-out benchmark on the active path; the signal is the
host's own usage.

### Zero-daemon lifecycle

No background process. The lifecycle recomputes at session start and ranks symbols by invocation
rate (calls since creation, per layer) rather than wall-clock age — so on ephemeral hosts a symbol
is never punished for never having had the chance to be used.

### Pure-additive, zero-intrusion

Enhancement happens only through a single plugin hook dispatcher plus writes to the skill
directory. Hooks observe and lazily curate; they never alter the host's skill registration or
recall path.

### Validate-before-any-write

Precise and safe concerns (safety scan, commit, name collisions) are deterministic; judgment calls
(duplication, correctness, value) are the LLM's. The model only proposes — landing is the
deterministic promoter's alone, and nothing reaches disk before it passes.

### One plugin, data split by layer

The final form is a single Claude Code plugin: one copy of the code, execution only from the hook
layer, and only data and state split global versus repo.

## Why not just let skills accumulate, or age them out on a timer?

Unbounded growth degrades recall — the more near-duplicate descriptions compete, the worse the host
picks. Timer-based archival assumes a resident process and a host that runs continuously; on
ephemeral, per-invocation hosts, elapsed time wrongly condemns symbols that simply had no turn to be
used. autoharness keeps the layer bounded by adherence instead.

| | Grow unbounded | Timer + daemon (e.g. [Hermes-Agent](https://github.com/NousResearch/Hermes-Agent)) | autoharness |
| --- | --- | --- | --- |
| Bounds the skill layer | No | Yes | Yes |
| Needs a resident daemon | No | Yes | No |
| Survival signal | None | Wall-clock inactivity | Invocation rate in use |
| Fair on ephemeral hosts | n/a | No | Yes |
| Author separated from validator | n/a | No | Yes |

Built by Tigerless Labs.

## License

[MIT](LICENSE)
