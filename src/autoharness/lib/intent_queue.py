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
UNREADABLE = "unreadable"  # key of the marker read() returns for a line that is not a JSON object


def _path(run_id, root=None):
    if not isinstance(run_id, str) or not _SAFE_RUN.match(run_id):
        raise ValueError(f"unsafe run id: {run_id!r}")
    return layer.state_dir(layer.PROJECT, root) / "intents" / f"{run_id}.jsonl"


def locked(run_id, root=None):
    """The run's append lock. A drain holds it across read → land → clear, so it never reads a line
    still being written and never clears one appended after its read."""
    p = _path(run_id, root)
    return lock.file_lock(p.with_suffix(p.suffix + ".lock"))


def append(run_id, intent, root=None):
    p = _path(run_id, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    # O_APPEND only keeps a write whole up to PIPE_BUF, and a staged skill body
    # runs well past that. Two overlapping reflector runs could interleave
    # mid-line, and the unparseable line jams every later drain of this run.
    with locked(run_id, root):
        # a torn tail with no newline would swallow this intent into its own unreadable line
        torn = p.exists() and p.stat().st_size > 0 and _last_byte(p) != b"\n"
        with p.open("a", encoding="utf-8") as f:
            f.write(("\n" if torn else "") + json.dumps(intent, ensure_ascii=False) + "\n")


def _last_byte(p):
    with p.open("rb") as f:
        f.seek(-1, 2)
        return f.read(1)


def read(run_id, root=None):
    p = _path(run_id, root)
    if not p.exists():
        return []
    out = []
    # written as UTF-8 whatever the locale; a torn append (crash or full disk mid-line) must not take
    # the whole queue down with it, so an unreadable line comes back as a marker the drain accounts
    # "\n" only: json.dumps escapes newlines inside strings but writes U+2028 and friends raw, and
    # splitlines() would cut one intent in two
    for line in p.read_text(encoding="utf-8", errors="replace").split("\n"):
        if not line.strip():
            continue
        try:
            intent = json.loads(line)
        except json.JSONDecodeError:
            intent = None
        out.append(intent if isinstance(intent, dict) else {UNREADABLE: line[:200]})
    return out


def clear(run_id, root=None):
    p = _path(run_id, root)
    if p.exists():
        p.unlink()


def orphans(root=None):
    d = layer.state_dir(layer.PROJECT, root) / "intents"
    if not d.exists():
        return []
    return sorted(f.stem for f in d.glob("*.jsonl"))
