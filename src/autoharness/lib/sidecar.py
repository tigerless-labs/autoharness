"""per-symbol sidecar: created_by / three-way counters (use / view / patch) / creation anchor / verification.

Single implementation, travels with the symbol directory across layers (promote/archive's mv carries
it, counters included, atomically). Operational metadata goes in the sidecar, not in SKILL.md
frontmatter (protects recall, does not pollute the user's work). created_by:agent is MNG's
membership key + the basis for promoter's "only touch self-produced" check.

Counter split (mng.md, hermes-parity direction C — mirrors Hermes use/view/patch): `use` = real load
via the Skill tool, the only lifecycle-rate numerator; `view` = main-session Read into the managed
dir, observation-only (mixes real consumption with curation browsing, so it only pardons at
graduation review); `patch` = promoter landed an update/patch. `reused_gen` marks the first use
after a patch (Hermes patch_generation pair) — the closest available "the skill helped" signal,
consumed by metrics only. Legacy single-numerator `calls` migrates into `use` on read, once.

ponytail: bumps are read-modify-write, not atomic across processes; the lock for concurrently
modifying the same symbol is deferred to mng (merged with promoter's single-writer lock); the unit
path is serial.
"""
import json

from autoharness.lib import atomic, layer

FILENAME = ".sidecar.json"


def path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / FILENAME


def _migrate(data):
    if "calls" in data:
        data["use"] = data.get("use", 0) + data.pop("calls")
    return data


def read(lyr, name, root=None):
    p = path(lyr, name, root)
    if not p.exists():
        return {}
    return _migrate(json.loads(p.read_text()))


def write(lyr, name, data, root=None):
    atomic.write_text(path(lyr, name, root), json.dumps(data, ensure_ascii=False, indent=2))


def create(lyr, name, anchor, root=None):
    data = {"created_by": "agent", "use": 0, "view": 0, "patch": 0,
            "anchor": int(anchor), "verification": None}
    write(lyr, name, data, root)
    return data


def _bump(lyr, name, key, root=None):
    data = read(lyr, name, root)
    data[key] = data.get(key, 0) + 1
    if key == "use" and data.get("patch", 0) > data.get("reused_gen", 0):
        data["reused_gen"] = data["patch"]  # first use after a patch = reuse-after-improvement
    write(lyr, name, data, root)
    return data[key]


def bump_use(lyr, name, root=None):
    return _bump(lyr, name, "use", root)


def bump_view(lyr, name, root=None):
    return _bump(lyr, name, "view", root)


def bump_patch(lyr, name, root=None):
    return _bump(lyr, name, "patch", root)


def is_agent_created(lyr, name, root=None):
    return read(lyr, name, root).get("created_by") == "agent"
