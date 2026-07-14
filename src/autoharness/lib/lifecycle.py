"""MNG decision: purely deterministic, call-rate + probation + graduation review + capacity contention → produces the "to-archive list". Touches no disk.

mng.md: the survival criterion is **call rate** (call count / layer requests since creation), not
wall-clock. Probation protects the new (denominator below the maturity threshold = live but not
evicted, not counted against the cap). Graduation review sits exactly at the probation boundary:
a mature symbol with zero calls is archived and never enters the pool — a full probation with no
use is genuine dormancy now that the numerator counts the Read path. Graduates (calls ≥ 1) die
only by capacity contention: when the mature pool exceeds the cap, archive the lowest by ascending
rate. The decision only reads cumulative watermarks (sidecar calls + anchor, layer request count),
so any repo's SessionStart reaches the same conclusion. on_session_start takes this list and runs
skill_store.archive on each.

ponytail: a rolling-window rate is deferred (open in mng.md).
"""


def _rate(calls, denom):
    return calls / denom if denom else 0.0


def evaluate(members, request_count, *, maturity, capacity):
    archive = set()
    survivors = []
    for m in members:
        denom = max(0, request_count - m.get("anchor", 0))
        if denom < maturity:
            continue  # probation: live, not evicted, not counted against the cap
        calls = m.get("calls", 0)
        if calls == 0:
            archive.add(m["name"])  # graduation review: a full probation with zero use never enters the pool
            continue
        survivors.append((_rate(calls, denom), m["name"]))
    if len(survivors) > capacity:
        survivors.sort(key=lambda rn: rn)  # ascending rate, ties broken stably by name
        archive.update(name for _, name in survivors[: len(survivors) - capacity])
    return sorted(archive)
