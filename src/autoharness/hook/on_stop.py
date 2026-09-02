"""CAP triggering (judged per turn): Stop hook + recursion guard + activity-count gate, fully deterministic, no LLM call.

cap.md (direction H): the numerator is the activity quantum — tool calls, accumulated by the
dispatcher at PreToolUse — not turns. Stop only reads the counter and judges the threshold
(a heavy turn triggers at its end; chat-only turns never advance the counter), emitting a trigger
verdict and resetting once reflect_every_n is reached. Cadence is deliberately conservative
(threshold errs sparse — precipitation is maintenance, not realtime; SessionEnd flush catches
the tail). Recursion guard: a reflector child session's Stop must neither re-trigger reflection
nor reset, otherwise infinite self-reflection. Bad/missing session-id -> no trigger (fail-safe).
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
        count = counters.session_count(session_id, root)
    except ValueError:
        return {"triggered": False, "reason": "bad_session"}
    if count >= n:
        counters.reset_session(session_id, root)
        return {"triggered": True, "session_id": session_id, "window_n": n, "count": count}
    return {"triggered": False, "session_id": session_id, "count": count, "n": n}
