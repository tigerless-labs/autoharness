"""per-run intent queue: writer=stage_skill(append) / reader=promoter(read+clear), one shared source.

Durable (recovers after a crash): only appends to a per-run file in the repo-layer state area, never
touches the skill tree. promoter runs read → land (atomic, idempotent) → clear: a crash between land
and clear leaves the file in place, and the next run's orphans scan recovers it (at-least-once +
atomic land = effectively exactly-once); in the extreme case where nothing ran, zero land (fail-safe).
"""
import json
import re

from autoharness.lib import layer, lock

_SAFE_RUN = re.compile(r"^[A-Za-z0-9_-]+$")


def _path(run_id, root=None):
    if not isinstance(run_id, str) or not _SAFE_RUN.match(run_id):
        raise ValueError(f"unsafe run id: {run_id!r}")
    return layer.state_dir(layer.PROJECT, root) / "intents" / f"{run_id}.jsonl"


def _recoverable_data(p):
    data = p.read_bytes()
    if data and not data.endswith(b"\n"):
        tail = data[data.rfind(b"\n") + 1:]
        try:
            json.loads(tail)
        except (ValueError, UnicodeDecodeError):
            # Only an unterminated final record is uncommitted. Complete malformed
            # lines remain visible to read() and fail closed rather than disappearing.
            return data[:data.rfind(b"\n") + 1]
    return data


def append(run_id, intent, root=None):
    p = _path(run_id, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    # O_APPEND only keeps a write whole up to PIPE_BUF, and a staged skill body
    # runs well past that. Two overlapping reflector runs could interleave
    # mid-line, and the unparseable line jams every later drain of this run.
    with lock.file_lock(p.with_suffix(p.suffix + ".lock")):
        if p.exists():
            data = _recoverable_data(p)
            # Remove a crash-torn tail before appending the next complete record.
            with p.open("r+b") as f:
                f.truncate(len(data))
            separator = "\n" if data and not data.endswith(b"\n") else ""
        else:
            separator = ""
        with p.open("a", encoding="utf-8") as f:
            f.write(separator + json.dumps(intent, ensure_ascii=False) + "\n")


def read(run_id, root=None):
    p = _path(run_id, root)
    if not p.exists():
        return []
    with lock.file_lock(p.with_suffix(p.suffix + ".lock")):
        if not p.exists():
            return []
        return [json.loads(line) for line in _recoverable_data(p).splitlines() if line.strip()]


def clear(run_id, root=None):
    p = _path(run_id, root)
    if p.exists():
        p.unlink()


def orphans(root=None):
    d = layer.state_dir(layer.PROJECT, root) / "intents"
    if not d.exists():
        return []
    return sorted(f.stem for f in d.glob("*.jsonl"))
