"""skill CRUD: atomic SKILL.md write + two-layer find (ambiguity error when the same name spans both layers) + apply delta + archive + orphan .tmp sweep.

Persistence uses atomic (same-dir temp + os.replace) in this one place, so live is never half-written.
find extends Hermes's `_find_skill` to the union of the global+project layers; the same name across
both layers → error (promoter uses this to disambiguate the layer when resolving update/delete).
apply_delta requires old_string to match uniquely (rejects both not-found and multiple-match
ambiguity), a deterministic rebuild. archive atomically moves symbol_dir into `.archive` (preserving
LED/sidecar); landing a delete and MNG (Phase 6) eviction share this one path.
"""
import os
import shutil

from autoharness.lib import atomic, layer

SKILL_FILE = "SKILL.md"


def skill_path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / SKILL_FILE


def write_body(lyr, name, body, root=None):
    atomic.write_text(skill_path(lyr, name, root), body)


def read_body(lyr, name, root=None):
    p = skill_path(lyr, name, root)
    return p.read_text() if p.exists() else None


def exists(lyr, name, root=None):
    return skill_path(lyr, name, root).exists()


def find(name, roots=None):
    roots = roots or {}
    hits = [lyr for lyr in layer.LAYERS if exists(lyr, name, roots.get(lyr))]
    if len(hits) > 1:
        raise ValueError(f"ambiguous skill {name!r} present in layers {hits}")
    return hits[0] if hits else None


def apply_delta(body, old_string, new_string):
    count = body.count(old_string)
    if count == 0:
        raise ValueError("delta old_string not found in live body")
    if count > 1:
        raise ValueError("delta old_string is ambiguous (multiple matches)")
    return body.replace(old_string, new_string, 1)


def remove(lyr, name, root=None):
    sdir = layer.symbol_dir(lyr, name, root)
    if sdir.exists():
        shutil.rmtree(sdir)


def archive(lyr, name, root=None):
    sdir = layer.symbol_dir(lyr, name, root)
    if not sdir.exists():
        return None
    dest = layer.archive_dir(lyr, root) / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    os.replace(sdir, dest)
    return dest


def restore(lyr, name, root=None):
    src = layer.archive_dir(lyr, root) / name
    if not src.exists():
        return None
    dest = layer.symbol_dir(lyr, name, root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    os.replace(src, dest)
    return dest


def sweep_orphans(lyr, root=None):
    skills = layer.skills_dir(lyr, root)
    if not skills.exists():
        return []
    removed = []
    for tmp in skills.rglob("*.tmp"):
        tmp.unlink()
        removed.append(tmp)
    return removed
