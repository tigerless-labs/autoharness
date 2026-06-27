"""per-symbol sidecar: created_by / numerator count (calls) / creation anchor (anchor) / verification.

Single implementation, travels with the symbol directory across layers (promote/archive's mv carries
it, numerator included, atomically). Operational metadata goes in the sidecar, not in SKILL.md
frontmatter (protects recall, does not pollute the user's work). created_by:agent is MNG's
membership key + the basis for promoter's "only touch self-produced" check.

ponytail: bump_calls is read-modify-write, not atomic across processes; the lock for concurrently
modifying the same symbol is deferred to mng (merged with promoter's single-writer lock); the unit
path is serial.
"""
import json

from autoharness.lib import atomic, layer

FILENAME = ".sidecar.json"


def path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / FILENAME


def read(lyr, name, root=None):
    p = path(lyr, name, root)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def write(lyr, name, data, root=None):
    atomic.write_text(path(lyr, name, root), json.dumps(data, ensure_ascii=False, indent=2))


def create(lyr, name, anchor, root=None):
    data = {"created_by": "agent", "calls": 0, "anchor": int(anchor), "verification": None}
    write(lyr, name, data, root)
    return data


def bump_calls(lyr, name, root=None):
    data = read(lyr, name, root)
    data["calls"] = data.get("calls", 0) + 1
    write(lyr, name, data, root)
    return data["calls"]


def is_agent_created(lyr, name, root=None):
    return read(lyr, name, root).get("created_by") == "agent"
