"""CAP triggering (per turn): Stop hook + recursion guard + count gate, fully deterministic, no LLM call.

cap.md: the only signal for "each response ended" is Stop. But Stop = per turn while an episode = a task
spanning many turns, so we do not spawn on every Stop — read a small int and +1 (O(1), no transcript
scan), and only emit a trigger verdict and reset once reflect_every_n is reached. The detached spawn
itself connects to Phase 5 spawn.py; this step only emits the trigger verdict — the window itself is
watermark-delimited by capture (raw bytes since the last reflection, zero overlap by construction).

Recursion guard: a reflector child session's Stop (CHILD_SESSION_ENV set) must neither re-trigger
reflection nor count, otherwise infinite self-reflection. Bad/missing session-id → no trigger
(fail-safe, does not crash the host hook).
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
