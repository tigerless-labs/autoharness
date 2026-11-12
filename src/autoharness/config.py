"""The single home for every knob + pointers to the two contract data files (architecture §config single point).

Calibration values (cadence / maturity threshold / capacity) are placeholders; empirical calibration
lives under experiments/. Tests assert only relationships (both layers present, >0), never absolute
values. Overridable via AUTOHARNESS_* env — for the e2e runbook to shrink the knobs (so graduation /
capacity contention fire within a short session); defaults fall back to the placeholders.
"""
import os
import shutil
import warnings
from pathlib import Path

from autoharness.lib import layer


def _int_env(name, default, minimum=None):
    try:
        value = int(os.environ[name])
    except KeyError:
        return default
    except ValueError:
        warnings.warn(f"{name}={os.environ[name]!r} is not a valid integer; using default {default}", stacklevel=2)
        return default
    if minimum is not None and value < minimum:
        warnings.warn(f"{name}={value} is below the minimum {minimum}; using default {default}", stacklevel=2)
        return default
    return value


def _str_env(name, default=None):
    """Read a non-empty string knob; an explicit blank is a typo, not an override."""
    try:
        raw = os.environ[name]
    except KeyError:
        return default
    value = raw.strip()
    if not value:
        fallback = repr(default) if default is not None else "the agent default"
        warnings.warn(f"{name} is empty; using {fallback}", stacklevel=2)
        return default
    return value


# trigger cadence, counted in the activity quantum (main-session tool calls, direction H) — not turns.
# Recalibrated with the numerator: the old turn-based 10 lands near 30-50 tool calls, and the standing
# ruling is to err sparse (precipitation is maintenance, and SessionEnd flushes the tail).
REFLECT_EVERY_N = _int_env("AUTOHARNESS_REFLECT_EVERY_N", 50, minimum=1)  # the window itself is watermark-delimited (capture)
# SessionEnd tail flushes are independent of the mid-session cadence above. Keep the historical
# flush-any-positive-tail behaviour by default, while allowing operators to decline tiny, expensive
# reflector runs. A skipped tail is deliberately discarded when the session counter is cleared.
MIN_FLUSH_N = _int_env("AUTOHARNESS_MIN_FLUSH_N", 1, minimum=1)
CONSOLIDATE_EVERY_N = _int_env("AUTOHARNESS_CONSOLIDATE_EVERY_N", 250)  # ponytail: placeholder, calibrate in experiments/; curator (content-level merge) beat, same quantum as REFLECT_EVERY_N and held sparser than it

# raw-capture byte caps (ponytail: placeholders, calibrate in experiments/): per transcript record,
# and per handoff window (tail kept) — bound tool dumps / base64 away from the child context.
CAPTURE_MAX_RECORD_BYTES = 4_000
CAPTURE_MAX_WINDOW_BYTES = 200_000
DIGEST_EXCHANGES = _int_env("AUTOHARNESS_DIGEST_EXCHANGES", 20, minimum=1)  # prior-context digest: exchanges before the window
DIGEST_MAX_RECORD_CHARS = 200
DIGEST_MAX_BYTES = 20_000

STAGE_MAX_BODY_BYTES = 100_000  # ponytail: placeholder, SKILL.md body cap; for instant feedback on stage_skill args
# altitude gate: SKILL.md body must read as a rule, not a transcript. A deterministic proxy for the
# reflector (the only LLM in the loop) actually distilling — non-blank body lines (ex-frontmatter)
# over this reject create/update; detail belongs in references/. ponytail: crude proxy, calibrate in experiments/.
SKILL_BODY_MAX_LINES = _int_env("AUTOHARNESS_SKILL_BODY_MAX_LINES", 25, minimum=1)
# description is the trigger: the host preloads name+description and matches recall on it, so a skill
# lives or dies here. Cap = Anthropic's documented 1024-char host limit (past it the host truncates).
SKILL_DESC_MAX_CHARS = _int_env("AUTOHARNESS_SKILL_DESC_MAX_CHARS", 1024)
# Description budget used by authoring validation and reflector indexes. SessionStart does not repeat
# descriptions: Claude Code already supplies every native skill name and full description.
INDEX_DESC_MAX_CHARS = _int_env("AUTOHARNESS_INDEX_DESC_MAX_CHARS", 60, minimum=4)
# Keep SessionStart's additive layer/category map below Claude Code's persisted-output threshold.
# The native skill list remains the complete recall surface when the compact map omits names.
SESSION_INDEX_MAX_BYTES = 1_600
# self-injection off switch: the index stops being emitted, everything else (lifecycle pass,
# use/view counters, the last-run summary) is untouched. Needed because the only other way to run
# without the index is to run without the plugin — which also removes the counters that measure the
# result. Also a legitimate operator knob for anyone unwilling to spend the context every session.
def _bool_env(name, default):
    val = _int_env(name, int(default))
    if val not in (0, 1):
        warnings.warn(
            f"{name}={val} should be 0 or 1; using default {int(default)}",
            stacklevel=2,
        )
        return bool(default)
    return bool(val)


INDEX_SUSPENDED = _bool_env("AUTOHARNESS_INDEX_SUSPENDED", False)
INDEX_BODY_PATHS = _bool_env("AUTOHARNESS_INDEX_BODY_PATHS", False)
DISABLE_GLOBAL = _bool_env("AUTOHARNESS_DISABLE_GLOBAL", False)


def active_layers():
    """Layers this deployment may inspect and manage."""
    return (layer.PROJECT,) if DISABLE_GLOBAL else layer.LAYERS


# folder-skill subfile caps (ponytail: placeholders like STAGE_MAX_BODY_BYTES, calibrate in experiments/)
STAGE_MAX_FILES = 8
STAGE_MAX_FILE_BYTES = 64_000
STAGE_MAX_FILES_TOTAL_BYTES = 256_000

# maturity threshold (denominator gate to graduate out of probation) / capacity cap, set per layer, independently tunable. global has a larger blast radius -> more conservative (smaller capacity).
MATURITY_THRESHOLD = {layer.GLOBAL: _int_env("AUTOHARNESS_MATURITY_GLOBAL", 300, minimum=0),
                      layer.PROJECT: _int_env("AUTOHARNESS_MATURITY_PROJECT", 100, minimum=0)}
CAPACITY = {layer.GLOBAL: _int_env("AUTOHARNESS_CAPACITY_GLOBAL", 20, minimum=0),
            layer.PROJECT: _int_env("AUTOHARNESS_CAPACITY_PROJECT", 50, minimum=0)}
# graduation-review suspend gate (direction C): while the recall surface is known-broken, archiving
# for zero use buries surfacing's failure — flip on to park the review, capacity contention unaffected.
GRADUATION_REVIEW_SUSPENDED = _bool_env("AUTOHARNESS_GRADUATION_SUSPENDED", False)
SNAPSHOT_KEEP = _int_env("AUTOHARNESS_SNAPSHOT_KEEP", 5, minimum=0)  # curator pre-run library snapshots per layer (mirrors Hermes)

# run-account notification (lib/notify), opt-in: the SessionStart summary is a session late and
# carries counts, not names. "desktop" = native notification; NOTIFY_CMD = argv fed the run record
# on stdin. Fail-open, fired after the queue is cleared; the timeout (whole seconds, per channel,
# floor 1) bounds how long a notifier can hold a drain — the interactive one runs inside Stop.
NOTIFY = os.environ.get("AUTOHARNESS_NOTIFY", "").strip().lower()
NOTIFY_CMD = os.environ.get("AUTOHARNESS_NOTIFY_CMD", "")
NOTIFY_TIMEOUT_S = max(1, _int_env("AUTOHARNESS_NOTIFY_TIMEOUT_S", 5))

# Name prefix every agent-authored skill must carry (empty = no constraint). A prefix keeps the
# library out of the namespace of hand-written and installed skills, so a create can never collide
# with one, and gives a repository a single ignore pattern for everything autoharness writes into it
# (the promoter adds that pattern to the repository's shared info/exclude on first landing).
SKILL_PREFIX = os.environ.get("AUTOHARNESS_SKILL_PREFIX", "")

# Launch child sessions (reflector / curator) without the user's settings sources: no other plugins,
# no user hooks, no project settings — only this plugin, loaded by --plugin-dir, running from its
# state directory so no project CLAUDE.md is read. Opt-in because it also drops settings a child may
# rely on, such as an apiKeyHelper; OAuth and environment credentials are unaffected.
CHILD_ISOLATION = _bool_env("AUTOHARNESS_CHILD_ISOLATION", False)

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_LIB = Path(__file__).parent / "lib"
REDACTION_RULES = _LIB / "redaction_rules.toml"  # secret/PII rule set, single source for CAP egress + LED
FORMAT_SPEC = _LIB / "format_spec.md"            # #416 single source for authoring + lint

CHILD_SESSION_ENV = "AUTOHARNESS_CHILD_SESSION"  # recursion-guard signal: set ONLY by spawn, read by CAP hooks (single source). Must be autoharness-owned: the host sets CLAUDE_CODE_CHILD_SESSION on every hook subprocess, so reusing it would gate every top-level turn.

# reflection carrier (direction G): "fork" resumes+forks the just-finished session — same model,
# parent's warm prefix cache, full-transcript replay, no materialized window. Stays "bundle"
# (window+digest via stdin to the registered subagent) until the fork cache-hit spike passes.
REFLECTOR_CARRIER = os.environ.get("AUTOHARNESS_CARRIER", "bundle")

REFLECTOR_AGENT = "autoharness:reflector"  # the --agent reference for spawn (plugin namespace, Phase 0 resolution pending live test)
CURATOR_AGENT = "autoharness:curator"      # the --agent reference for the periodic consolidation pass (same spawn chain as reflector)
# Unset means "let the agent frontmatter decide" (currently `model: haiku`), preserving the exact
# historical command line. An explicit value becomes a --model override for the maintenance session.
REFLECTOR_MODEL = _str_env("AUTOHARNESS_REFLECTOR_MODEL")
CURATOR_MODEL = _str_env("AUTOHARNESS_CURATOR_MODEL")
CLAUDE_BIN = shutil.which("claude") or "claude"  # the child-session executable for spawn; which() honours PATHEXT so Windows resolves claude.cmd (bare "claude" raises WinError 2 under CreateProcess); overridable in tests
RUN_ID_ENV = "AUTOHARNESS_RUN_ID"           # spawn injects the intent-queue run_id into the child session via env (read by stage_skill)
# The queue for intents staged from a live user session (/learn, or the model acting on its own).
# spawn injects a run id into every child it launches and drains that run when the child exits; a
# user's own session has neither, so before this existed stage_skill refused with "unsafe run id"
# and the shipped learn skill could never land anything. The main session's Stop drains this queue.
INTERACTIVE_RUN_ID = "interactive"
PROJECT_ROOT_ENV = layer.PROJECT_ROOT_ENV  # same: the project layer root, where the queue is persisted (layer resolves it)
