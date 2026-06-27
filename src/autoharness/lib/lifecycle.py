"""MNG decision: purely deterministic, call-rate + probation + capacity contention → produces the "to-archive list". Touches no disk.

mng.md: the survival criterion is **call rate** (call count / layer requests since creation), not
wall-clock. Probation protects the new (denominator below the maturity threshold = live but not
evicted, not counted against the cap); graduate-and-review (still calls==0 at full sample = archived
on the spot); when the mature survivor pool exceeds the cap, archive the lowest by ascending rate.
The decision only reads cumulative watermarks (sidecar calls + anchor, layer request count), so any
repo's SessionStart reaches the same conclusion. on_session_start takes this list and runs
skill_store.archive on each.

ponytail: an absolute floor rule (a hard floor Y beyond graduate-review) and a rolling-window rate
are deferred (open in mng.md).
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
            archive.add(m["name"])  # graduate-and-review: given enough chances, still zero calls
            continue
        survivors.append((_rate(calls, denom), m["name"]))
    if len(survivors) > capacity:
        survivors.sort(key=lambda rn: rn)  # ascending rate, ties broken stably by name
        archive.update(name for _, name in survivors[: len(survivors) - capacity])
    return sorted(archive)
