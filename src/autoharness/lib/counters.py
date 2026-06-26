"""会话计数器（CAP 触发：每 Stop +1、满 N 清零）+ 层请求计数器（MNG 分母：每回合 +1）。

单一实现、按层；O(1) 读改写、即时持久（每个 hook 是独立短进程，内存留不住）。分子（被调
次数）归 sidecar（随符号走层），不在此。会话计数住 repo 层 state 区（cap.md：session 级、
落本仓 .claude，不入 live skills）。

ponytail: 读-改-写跨进程非原子；global 请求计数器多 repo 并发写的锁见 mng 待解。
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
