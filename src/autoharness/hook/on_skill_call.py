"""MNG numerator instrumentation: at `PreToolUse(Skill)` and `PreToolUse(Read)` into a managed symbol directory, +1 the used symbol's sidecar calls, pure observation, no interception.

mng.md: the rate numerator = number of uses, stored in the used symbol's sidecar, layer-agnostic
(identity decides which layer). Measured (experiments/E8_numerator_capture): the model's dominant
consumption path is a direct Read of SKILL.md / subfiles, almost never the Skill tool, so the Read
path is the load-bearing half of the numerator. **Zero-intrusion red line — count only self-produced
symbols**, never write a sidecar for native / user skills (touching them violates "do not touch the
host's work"). Recursion guard same as CAP: a reflector child session is not counted. Bad / unknown /
same-name ambiguous symbols and reads under `.archive` fail-safe without crashing the host hook.

ponytail: the exact key for a symbol's identity in the event = Phase 0 spike (mng.md open); for now extract with field-tolerant fallbacks over a few candidate keys.
"""
import os
from pathlib import Path

from autoharness import config
from autoharness.lib import layer, sidecar, skill_store


def _skill_name(event):
    nested = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    for src in (event, nested):
        for key in ("skill_name", "skill", "name"):
            v = src.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return None


def _name_from_read_path(event, roots):
    nested = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    file_path = nested.get("file_path") or event.get("file_path")
    if not isinstance(file_path, str) or not file_path.strip():
        return None
    target = Path(file_path)
    for lyr in layer.LAYERS:
        base = layer.skills_dir(lyr, roots.get(lyr))
        try:
            rel = target.resolve().relative_to(base.resolve())
        except (ValueError, OSError):
            continue
        if len(rel.parts) > 1 and rel.parts[0] != ".archive":
            return rel.parts[0]
    return None


def _count(name, roots):
    if not name:
        return {"counted": False, "reason": "no_skill"}
    try:
        lyr = skill_store.find(name, roots)
    except ValueError:
        return {"counted": False, "reason": "bad_or_ambiguous"}
    if lyr is None:
        return {"counted": False, "reason": "not_managed"}
    root = roots.get(lyr)
    if not sidecar.is_agent_created(lyr, name, root):
        return {"counted": False, "reason": "not_agent_created"}
    calls = sidecar.bump_calls(lyr, name, root)
    return {"counted": True, "level": lyr, "name": name, "calls": calls}


def on_skill_call(event, *, roots=None):
    if os.environ.get(config.CHILD_SESSION_ENV):
        return {"counted": False, "reason": "recursion_guard"}
    return _count(_skill_name(event), roots or {})


def on_skill_read(event, *, roots=None):
    if os.environ.get(config.CHILD_SESSION_ENV):
        return {"counted": False, "reason": "recursion_guard"}
    roots = roots or {}
    return _count(_name_from_read_path(event, roots), roots)
