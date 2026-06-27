"""MNG numerator instrumentation: at `PreToolUse(Skill)`, +1 the called symbol's sidecar calls, pure observation, no interception.

mng.md: the rate numerator = number of calls, stored in the called symbol's sidecar, layer-agnostic
(identity decides which layer). **Zero-intrusion red line — count only self-produced symbols**, never
write a sidecar for native / user skills (touching them violates "do not touch the host's work").
Recursion guard same as CAP: a reflector child session is not counted. Bad / unknown / same-name
ambiguous symbols fail-safe without crashing the host hook.

ponytail: the exact key for a symbol's identity in the event = Phase 0 spike (mng.md open); for now extract with field-tolerant fallbacks over a few candidate keys.
"""
import os

from autoharness import config
from autoharness.lib import sidecar, skill_store


def _skill_name(event):
    nested = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    for src in (event, nested):
        for key in ("skill_name", "skill", "name"):
            v = src.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return None


def on_skill_call(event, *, roots=None):
    if os.environ.get(config.CHILD_SESSION_ENV):
        return {"counted": False, "reason": "recursion_guard"}
    roots = roots or {}
    name = _skill_name(event)
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
