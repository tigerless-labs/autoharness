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


REFLECT_EVERY_N = _int_env("AUTOHARNESS_REFLECT_EVERY_N", 10)  # trigger cadence == size of the window fed to REF

STAGE_MAX_BODY_BYTES = 100_000  # ponytail: placeholder, SKILL.md body cap; for instant feedback on stage_skill args

# folder-skill subfile caps (ponytail: placeholders like STAGE_MAX_BODY_BYTES, calibrate in experiments/)
STAGE_MAX_FILES = 8
STAGE_MAX_FILE_BYTES = 64_000
STAGE_MAX_FILES_TOTAL_BYTES = 256_000

# maturity threshold (denominator gate to graduate out of probation) / capacity cap, set per layer, independently tunable. global has a larger blast radius -> more conservative (smaller capacity).
MATURITY_THRESHOLD = {layer.GLOBAL: _int_env("AUTOHARNESS_MATURITY_GLOBAL", 50),
                      layer.PROJECT: _int_env("AUTOHARNESS_MATURITY_PROJECT", 20)}
CAPACITY = {layer.GLOBAL: _int_env("AUTOHARNESS_CAPACITY_GLOBAL", 20),
            layer.PROJECT: _int_env("AUTOHARNESS_CAPACITY_PROJECT", 50)}

_LIB = Path(__file__).parent / "lib"
REDACTION_RULES = _LIB / "redaction_rules.toml"  # secret/PII rule set, single source for CAP egress + LED
FORMAT_SPEC = _LIB / "format_spec.md"            # #416 single source for authoring + lint

CHILD_SESSION_ENV = "AUTOHARNESS_CHILD_SESSION"  # recursion-guard signal: set ONLY by spawn, read by CAP hooks (single source). Must be autoharness-owned: the host sets CLAUDE_CODE_CHILD_SESSION on every hook subprocess, so reusing it would gate every top-level turn.

REFLECTOR_AGENT = "autoharness:reflector"  # the --agent reference for spawn (plugin namespace, Phase 0 resolution pending live test)
CLAUDE_BIN = "claude"                       # the child-session executable for spawn; PATH resolution, overridable in tests
RUN_ID_ENV = "AUTOHARNESS_RUN_ID"           # spawn injects the intent-queue run_id into the child session via env (read by stage_skill)
PROJECT_ROOT_ENV = "AUTOHARNESS_PROJECT_ROOT"  # same: repo root (where the queue is persisted)
