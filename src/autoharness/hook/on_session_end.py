"""CAP triggering (wrap-up): SessionEnd flushes the remainder + self-deletes the session counter.

By default every positive tail is flushed. AUTOHARNESS_MIN_FLUSH_N lets an operator explicitly
discard a smaller tail rather than pay for a full reflector run; **the current count value still
tells REF exactly how many to feed** (window N == count, not the threshold). The session counter
self-deletes either way. Recursion guard same as on_stop: a reflector child session's SessionEnd
does not flush.

ponytail: orphan counters of crashed sessions are GC'd lazily on SessionStart (landed when this file is built in Phase 6, cap.md open).
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
    if count >= config.MIN_FLUSH_N:
        return {"triggered": True, "session_id": session_id, "window_n": count, "count": count}
    if count > 0:
        return {
            "triggered": False,
            "reason": "below_min_flush",
            "session_id": session_id,
            "count": count,
            "minimum": config.MIN_FLUSH_N,
        }
    return {"triggered": False, "session_id": session_id, "count": 0}
