"""per-run intent queue: writer=stage_skill(append) / reader=promoter(take+drop), one shared source.

Durable (recovers after a crash): only appends to a per-run file in the repo-layer state area, never
touches the skill tree. promoter runs claim → land (atomic, idempotent) → drop: a crash between
claim and drop leaves the claim file in place, and the next run's orphans scan recovers it
(at-least-once + atomic land = effectively exactly-once); in the extreme case where nothing ran,
zero land (fail-safe).
"""
import json
import os
import re

from autoharness.lib import layer, lock

_SAFE_RUN = re.compile(r"^[A-Za-z0-9_-]+$")


def _path(run_id, root=None):
    if not isinstance(run_id, str) or not _SAFE_RUN.match(run_id):
        raise ValueError(f"unsafe run id: {run_id!r}")
    return layer.state_dir(layer.PROJECT, root) / "intents" / f"{run_id}.jsonl"


def append(run_id, intent, root=None):
    p = _path(run_id, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    # O_APPEND only keeps a write whole up to PIPE_BUF, and a staged skill body
    # runs well past that. Two overlapping reflector runs could interleave
    # mid-line, and the unparseable line jams every later drain of this run.
    with lock.file_lock(p.with_suffix(p.suffix + ".lock")):
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(intent, ensure_ascii=False) + "\n")


def read(run_id, root=None):
    p = _path(run_id, root)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def clear(run_id, root=None):
    p = _path(run_id, root)
    if p.exists():
        p.unlink()


def _claim_path(run_id, root=None):
    p = _path(run_id, root)
    return p.with_name(f"{p.stem}.draining")


def _live_path(run_id, root=None):
    p = _path(run_id, root)
    return p.with_name(f"{p.stem}.live")


def take(run_id, root=None):
    """Claim the run's queue and return its intents, oldest first.

    The claim renames <run>.jsonl to <run>.draining under the append lock, so an append that
    lands after the claim starts a fresh <run>.jsonl for the run's own drain instead of racing
    the drain's clear (a foreign drain of a live run's queue used to unlink a staged intent
    unread). A .draining left by a drain that crashed before drop() is read first: the same
    intents again, harmless because landing is idempotent, and read before the fresh batch so
    run ordering holds.
    """
    p = _path(run_id, root)
    claimed = _claim_path(run_id, root)
    lines = claimed.read_text().splitlines() if claimed.exists() else []
    with lock.file_lock(p.with_suffix(p.suffix + ".lock")):
        if p.exists():
            lines += p.read_text().splitlines()
            os.replace(p, claimed)
    return [json.loads(line) for line in lines if line.strip()]


def drop(run_id, root=None):
    """Discard the claimed batch once every intent in it landed and was accounted."""
    claimed = _claim_path(run_id, root)
    if claimed.exists():
        claimed.unlink()


def live_lock(run_id, root=None):
    """The run's liveness marker: held by the spawn parent for the child's whole run plus its
    own drain, so a foreign drain can tell an abandoned queue from a run that will drain itself."""
    return lock.file_lock(_live_path(run_id, root))


def is_live(run_id, root=None):
    """True while some process holds the run's live lock (its spawn parent is still working)."""
    return lock.held(_live_path(run_id, root))


def orphans(root=None):
    """Undrained run ids: a live queue, or a claim a crashed drain never dropped."""
    d = layer.state_dir(layer.PROJECT, root) / "intents"
    if not d.exists():
        return []
    return sorted({f.stem for pattern in ("*.jsonl", "*.draining") for f in d.glob(pattern)})
