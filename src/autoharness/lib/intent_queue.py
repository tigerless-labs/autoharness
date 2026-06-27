"""per-run intent queue: writer=stage_skill(append) / reader=promoter(read+clear), one shared source.

Durable (recovers after a crash): only appends to a per-run file in the repo-layer state area, never
touches the skill tree. promoter runs read → land (atomic, idempotent) → clear: a crash between land
and clear leaves the file in place, and the next run's orphans scan recovers it (at-least-once +
atomic land = effectively exactly-once); in the extreme case where nothing ran, zero land (fail-safe).
"""
import json
import re

from autoharness.lib import layer

_SAFE_RUN = re.compile(r"^[A-Za-z0-9_-]+$")


def _path(run_id, root=None):
    if not isinstance(run_id, str) or not _SAFE_RUN.match(run_id):
        raise ValueError(f"unsafe run id: {run_id!r}")
    return layer.state_dir(layer.PROJECT, root) / "intents" / f"{run_id}.jsonl"


def append(run_id, intent, root=None):
    p = _path(run_id, root)
    p.parent.mkdir(parents=True, exist_ok=True)
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


def orphans(root=None):
    d = layer.state_dir(layer.PROJECT, root) / "intents"
    if not d.exists():
        return []
    return sorted(f.stem for f in d.glob("*.jsonl"))
