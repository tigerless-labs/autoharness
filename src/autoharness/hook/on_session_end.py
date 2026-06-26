"""CAP 触发（收尾）：SessionEnd flush 余量 + 自删会话计数器。

cap.md：不满阈值的尾巴若不 flush 会永远丢；故会话结束时计数 > 0 即反思余量，**当前计数值
正好告诉 REF 喂几个**（窗口 N == 计数、非阈值）。随后会话计数器随 session 生死自删。
递归 guard 同 on_stop：reflector 子会话的 SessionEnd 不 flush。

ponytail: 崩溃 session 的孤儿计数器走 SessionStart 惰性 GC（Phase 6 该文件建时落，cap.md 待解）。
"""
import os

from autoharness import config
from autoharness.lib import counters


def on_session_end(event, *, root=None):
    if os.environ.get(config.CHILD_SESSION_ENV):
        return {"triggered": False, "reason": "recursion_guard"}
    session_id = event.get("session_id")
    if not session_id:
        return {"triggered": False, "reason": "no_session"}
    try:
        count = counters.session_count(session_id, root)
    except ValueError:
        return {"triggered": False, "reason": "bad_session"}
    counters.clear_session(session_id, root)
    if count > 0:
        return {"triggered": True, "session_id": session_id, "window_n": count, "count": count}
    return {"triggered": False, "session_id": session_id, "count": 0}
