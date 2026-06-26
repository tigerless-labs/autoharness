# autoharness

**A per-symbol maintenance optimizer for an agent's skill layer — it learns skills from real
runs and lets them earn their keep by being *adhered to in use*, not by an offline eval score.**

autoharness watches a host agent's own sessions, distills each episode into a skill, and lands it
into the native skill directory (`.claude/skills`) where the host recalls it normally. Skills that
keep getting invoked survive; ones that go unused or get contradicted are archived. It runs as a
**pure-additive, zero-daemon Claude Code plugin** — it never touches the host's skill load/recall
path, only observes via hooks and writes to disk.

Closest neighbor is [Hermes-Agent](https://github.com/NousResearch/Hermes-Agent); the wedge:
Hermes ages skills out on a wall-clock timer behind a resident daemon. autoharness has **no daemon**
(lazy `SessionStart` recompute) and judges symbols by **invocation rate**, not elapsed time — so on
ephemeral hosts a skill is never punished for "never had the chance to be used."

> **Status: design-stage.** The architecture is settled and documented; the plugin is not built yet.
> No install path exists today — see [docs/](docs/index.md) for the design, [docs/plans/roadmap.md](docs/plans/roadmap.md) for the build order.

---

## How it works

A learning pipeline runs *beside* the host. The host's native skill recall is untouched.

| Component | Role |
|---|---|
| **CAP** capture | Hook-driven dumb pipe: grabs each turn (user input + agent output + tool I/O), redacts at egress, points back at the host log instead of copying it. |
| **REF** reflect | At an episode boundary, **compare-first**: reads the existing skill index, decides add / merge / patch / delete, and emits an *intent* (body or delta + reason/evidence). It can only propose — it has no write tools. |
| **promoter** validate·store | The only writer. Shapes the intent in memory, runs a deterministic linter (safety, structure, ledger, completeness, self-authored-only), and **only on pass** does an atomic rename into the live skill dir. **Validate-before-any-write** — nothing hits disk until it's clean. |
| **MNG** lifecycle | Deterministic, daemon-free. Ranks symbols by invocation rate per provenance layer; protects new ones (probation), archives the weakest when a mature pool is over capacity. Archives, never deletes. |
| **LED** ledger | Per-symbol append-only sidecar: why each symbol was born/changed, with evidence and a reflection watermark. Kept out of the skill body so recall stays clean. |

```
┌─── host agent (host-agnostic) — autoharness is pure-additive, zero-intrusion ───┐
│   session runs   ·   native skill recall (.claude/skills; name+desc → recall)   │
└──┬───────────────────────────────────────────────────────────────────▲─────────┘
   │ CAP: hooks observe                              symbols = native skills, host recalls them
   ▼                                                                     │
 CAP capture ──► REF reflect (compare-first, ──► promoter (admission: validate in memory,
 (hooks)         emits intent, no write tools)    atomic write on pass) ─┘
   │ trace pointer                                      │ append LED
   ▼                                          MNG lifecycle      LED ledger (sidecar)
 [host log]
```

**Invariants:** pure-additive / zero-intrusion · author ≠ validator (REF proposes, a deterministic
linter gates) · precise & safe → deterministic, judgment → LLM · validate-before-any-write ·
model only proposes, landing is the promoter's alone.

The final shape is a **single Claude Code plugin**: one copy of the code, execution only from the
plugin's hook layer, and only data/state split global vs repo. See [docs/research-loom/design/architecture.md](docs/research-loom/design/architecture.md).

## Documentation

| | |
|---|---|
| [docs/](docs/index.md) | Documentation map — single entry point. |
| [design spine](docs/research-loom/design/spine.md) | Principle + pipeline + global invariants + architecture diagram. |
| [architecture](docs/research-loom/design/architecture.md) | Code structure / file tree of the plugin. |
| [research-loom](docs/research-loom/index.md) | The literature→design workspace: every cited source, synthesized into the design across five provenance-linked layers. |
| [roadmap](docs/plans/roadmap.md) | Implementation roadmap, test strategy, CI gates. |
| [TODO](docs/TODO.md) | Tracked follow-ups. |

## License

[MIT](LICENSE).
