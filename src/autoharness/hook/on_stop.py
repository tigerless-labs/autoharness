"""CAP 触发（每轮）：Stop hook + 递归 guard + 计数闸，全确定性、不调 LLM。

cap.md：唯一拿到「每次响应结束」的信号是 Stop。但 Stop=每轮、episode=跨多轮任务，故不每
Stop 都 spawn——读小 int +1（O(1)、不扫 transcript），满 reflect_every_n 才出触发裁决并清零。
detached spawn 本身接 Phase 5 spawn.py；本步只出「是否触发 + 窗口 N」，spawn 据此调
capture.materialize（窗口 N == 阈值，与触发节奏同数、零重叠）。

递归 guard：reflector 子会话（CHILD_SESSION_ENV 有值）的 Stop 不得再触发反思、且不计数，
否则无限自反思。坏/缺 session-id → 不触发（fail-safe，不崩宿主 hook）。
"""
import os

from autoharness import config
from autoharness.lib import counters


def on_stop(event, *, root=None, n=None):
    if os.environ.get(config.CHILD_SESSION_ENV):
        return {"triggered": False, "reason": "recursion_guard"}
    session_id = event.get("session_id")
    if not session_id:
        return {"triggered": False, "reason": "no_session"}
    n = n or config.REFLECT_EVERY_N
    try:
        count = counters.bump_session(session_id, root)
    except ValueError:
        return {"triggered": False, "reason": "bad_session"}
    if count >= n:
        counters.reset_session(session_id, root)
        return {"triggered": True, "session_id": session_id, "window_n": n, "count": count}
    return {"triggered": False, "session_id": session_id, "count": count, "n": n}
