"""The single home for every knob + pointers to the two contract data files (architecture §config single point).

Calibration values (cadence / maturity threshold / capacity) are placeholders; empirical calibration
lives under experiments/. Tests assert only relationships (both layers present, >0), never absolute
values. Overridable via AUTOHARNESS_* env — for the e2e runbook to shrink the knobs (so graduation /
capacity contention fire within a short session); defaults fall back to the placeholders.
"""
import os
from pathlib import Path

from autoharness.lib import layer


def _int_env(name, default):
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


# trigger cadence, counted in the activity quantum (main-session tool calls, direction H) — not turns.
# Recalibrated with the numerator: the old turn-based 10 lands near 30-50 tool calls, and the standing
# ruling is to err sparse (precipitation is maintenance, and SessionEnd flushes the tail).
REFLECT_EVERY_N = _int_env("AUTOHARNESS_REFLECT_EVERY_N", 50)  # the window itself is watermark-delimited (capture)
CONSOLIDATE_EVERY_N = _int_env("AUTOHARNESS_CONSOLIDATE_EVERY_N", 250)  # ponytail: placeholder, calibrate in experiments/; curator (content-level merge) beat, same quantum as REFLECT_EVERY_N and held sparser than it

# raw-capture byte caps (ponytail: placeholders, calibrate in experiments/): per transcript record,
# and per handoff window (tail kept) — bound tool dumps / base64 away from the child context.
CAPTURE_MAX_RECORD_BYTES = 4_000
CAPTURE_MAX_WINDOW_BYTES = 200_000
DIGEST_EXCHANGES = _int_env("AUTOHARNESS_DIGEST_EXCHANGES", 20)  # prior-context digest: exchanges before the window
DIGEST_MAX_RECORD_CHARS = 200
DIGEST_MAX_BYTES = 20_000

STAGE_MAX_BODY_BYTES = 100_000  # ponytail: placeholder, SKILL.md body cap; for instant feedback on stage_skill args
# altitude gate: SKILL.md body must read as a rule, not a transcript. A deterministic proxy for the
# reflector (the only LLM in the loop) actually distilling — non-blank body lines (ex-frontmatter)
# over this reject create/update; detail belongs in references/. ponytail: crude proxy, calibrate in experiments/.
SKILL_BODY_MAX_LINES = _int_env("AUTOHARNESS_SKILL_BODY_MAX_LINES", 25)
# description is the trigger: the host preloads name+description and matches recall on it, so a skill
# lives or dies here. Cap = Anthropic's documented 1024-char host limit (past it the host truncates).
SKILL_DESC_MAX_CHARS = _int_env("AUTOHARNESS_SKILL_DESC_MAX_CHARS", 1024)
# self-injected recall index (SessionStart additionalContext): per-line description truncation,
# mirroring Hermes's tier-0 index discipline — the index is a scan surface, not the full trigger text.
INDEX_DESC_MAX_CHARS = _int_env("AUTOHARNESS_INDEX_DESC_MAX_CHARS", 60)
# injection budget: rendered index lines (category headers + entries). Over it, whole categories
# collapse to one names-only line, least-earned first — never removed (mng.md: a name that leaves the
# index is a capability the model stops reaching for). 0 = no budget, the shipping default until the
# recall baseline exists: the ranking eats use counts, and while surfacing itself is unverified a low
# count may only mean "never offered".
INDEX_MAX_LINES = _int_env("AUTOHARNESS_INDEX_MAX_LINES", 0)

# folder-skill subfile caps (ponytail: placeholders like STAGE_MAX_BODY_BYTES, calibrate in experiments/)
STAGE_MAX_FILES = 8
STAGE_MAX_FILE_BYTES = 64_000
STAGE_MAX_FILES_TOTAL_BYTES = 256_000

# maturity threshold (denominator gate to graduate out of probation) / capacity cap, set per layer, independently tunable. global has a larger blast radius -> more conservative (smaller capacity).
MATURITY_THRESHOLD = {layer.GLOBAL: _int_env("AUTOHARNESS_MATURITY_GLOBAL", 300),
                      layer.PROJECT: _int_env("AUTOHARNESS_MATURITY_PROJECT", 100)}
CAPACITY = {layer.GLOBAL: _int_env("AUTOHARNESS_CAPACITY_GLOBAL", 20),
            layer.PROJECT: _int_env("AUTOHARNESS_CAPACITY_PROJECT", 50)}
# graduation-review suspend gate (direction C): while the recall surface is known-broken, archiving
# for zero use buries surfacing's failure — flip on to park the review, capacity contention unaffected.
GRADUATION_REVIEW_SUSPENDED = bool(_int_env("AUTOHARNESS_GRADUATION_SUSPENDED", 0))
SNAPSHOT_KEEP = _int_env("AUTOHARNESS_SNAPSHOT_KEEP", 5)  # curator pre-run library snapshots per layer (mirrors Hermes)

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
CLAUDE_BIN = "claude"                       # the child-session executable for spawn; PATH resolution, overridable in tests
RUN_ID_ENV = "AUTOHARNESS_RUN_ID"           # spawn injects the intent-queue run_id into the child session via env (read by stage_skill)
PROJECT_ROOT_ENV = "AUTOHARNESS_PROJECT_ROOT"  # same: repo root (where the queue is persisted)
