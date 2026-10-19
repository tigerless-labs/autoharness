"""skill CRUD: atomic SKILL.md write + two-layer find (ambiguity error when the same name spans both layers) + apply delta + archive + orphan .tmp sweep.

Persistence uses atomic (same-dir temp + os.replace) in this one place, so live is never half-written.
find extends Hermes's `_find_skill` to the union of the global+project layers; the same name across
both layers → error (promoter uses this to disambiguate the layer when resolving update/delete).
apply_delta requires old_string to match uniquely (rejects both not-found and multiple-match
ambiguity), a deterministic rebuild. archive atomically moves symbol_dir into `.archive` (preserving
LED/sidecar); landing a delete and MNG (Phase 6) eviction share this one path.
"""
import json
import os
import shutil
import time

from autoharness import config
from autoharness.lib import atomic, layer

SKILL_FILE = "SKILL.md"


def _collision_safe_dest(dest):
    if not dest.exists():
        return dest
    suffix = time.strftime("%Y%m%dT%H%M%S")
    candidate = dest.with_name(f"{dest.name}.{suffix}")
    counter = 2
    while candidate.exists():
        candidate = dest.with_name(f"{dest.name}.{suffix}.{counter}")
        counter += 1
    return candidate


def skill_path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / SKILL_FILE


def write_body(lyr, name, body, root=None):
    atomic.write_text(skill_path(lyr, name, root), body)


def read_body(lyr, name, root=None):
    p = skill_path(lyr, name, root)
    return p.read_text(encoding="utf-8") if p.exists() else None


def exists(lyr, name, root=None):
    return skill_path(lyr, name, root).exists()


def find(name, roots=None):
    roots = roots or {}
    hits = [lyr for lyr in config.active_layers() if exists(lyr, name, roots.get(lyr))]
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
    dest = _collision_safe_dest(dest)
    os.replace(sdir, dest)
    return dest


def restore(lyr, name, root=None):
    src = layer.archive_dir(lyr, root) / name
    if not src.exists():
        return None
    dest = layer.symbol_dir(lyr, name, root)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest = _collision_safe_dest(dest)
    os.replace(src, dest)
    return dest


# an atomic write lives as a .tmp for milliseconds; a younger one may be another hook's write in flight
ORPHAN_TMP_MIN_AGE_S = 60


def _ours(d):
    """A skill dir autoharness wrote (its sidecar says so), or the debris of one of its creates that died
    inside the sidecar write (nothing but .tmp files). Anyone else's skill is left alone."""
    if d.is_symlink() or not d.is_dir():
        return False
    try:
        meta = json.loads((d / ".sidecar.json").read_text(encoding="utf-8"))
        return isinstance(meta, dict) and meta.get("created_by") == "agent"
    except (OSError, ValueError):
        pass
    try:
        return all(p.is_file() and p.suffix == ".tmp" for p in d.iterdir())
    except OSError:
        return False  # unreadable: not something we can tell is ours


def _listing(d):
    try:
        return list(d.iterdir())
    except OSError:
        return []  # an unreadable dir: nothing to sweep there, and the drain must still run


def sweep_orphans(lyr, root=None):
    skills = layer.skills_dir(lyr, root)
    if not skills.exists():
        return []
    removed = []
    cutoff = time.time() - ORPHAN_TMP_MIN_AGE_S
    archive = layer.archive_dir(lyr, root)
    try:  # a linked .archive leads outside the layer: never walk it; an unreadable layer has none to walk
        walk_archive = archive.is_dir() and not archive.is_symlink()
    except OSError:
        walk_archive = False
    dirs = [*_listing(skills), *(_listing(archive) if walk_archive else [])]
    for tmp in (t for d in dirs if _ours(d) for t in d.rglob("*.tmp")):
        try:
            if tmp.stat().st_mtime > cutoff:
                continue
            tmp.unlink()
        except FileNotFoundError:
            continue  # its writer renamed it into place meanwhile
        removed.append(tmp)
    return removed
