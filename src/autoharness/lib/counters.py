"""Session counter (CAP trigger: +1 per Stop, reset at N) + per-layer request counter (MNG denominator: +1 per turn).

Single implementation, per-layer; O(1) read-modify-write, persisted immediately (each hook is a
separate short-lived process, nothing survives in memory). The numerator (call count) belongs to
sidecar (travels with the symbol across layers), not here. Session counts live in the repo-layer
state area (cap.md: session-scoped, written to this repo's .claude, not into live skills).

ponytail: read-modify-write is not atomic across processes; the lock for the global request counter
under concurrent multi-repo writes is deferred to mng.
"""
import re

from autoharness.lib import atomic, layer

_SAFE_SESSION = re.compile(r"^[A-Za-z0-9_-]+$")


def _read_int(p):
    try:
        return int(p.read_text().strip())
    except (FileNotFoundError, ValueError):
        return 0


def _bump(p, delta=1):
    value = _read_int(p) + delta
    atomic.write_text(p, str(value))
    return value


def request_count(lyr, root=None):
    return _read_int(layer.state_dir(lyr, root) / "requests")


def bump_request(lyr, root=None):
    return _bump(layer.state_dir(lyr, root) / "requests")


def _session_path(session_id, root=None):
    if not isinstance(session_id, str) or not _SAFE_SESSION.match(session_id):
        raise ValueError(f"unsafe session id: {session_id!r}")
    return layer.state_dir(layer.PROJECT, root) / f"session-{session_id}"


def session_count(session_id, root=None):
    return _read_int(_session_path(session_id, root))


def bump_session(session_id, root=None):
    return _bump(_session_path(session_id, root))


def reset_session(session_id, root=None):
    atomic.write_text(_session_path(session_id, root), "0")


def clear_session(session_id, root=None):
    p = _session_path(session_id, root)
    if p.exists():
        p.unlink()
