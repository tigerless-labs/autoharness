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

import hashlib


def _rate(use, denom):
    return use / denom if denom else 0.0


def evaluate(members, request_count, *, maturity, capacity, review_suspended=False):
    archive = set()
    survivors = []
    for m in members:
        denom = max(0, request_count - m.get("anchor", 0))
        if denom < maturity:
            continue  # probation: live, not evicted, not counted against the cap
        use = m.get("use", m.get("calls", 0))  # rate eats use only; legacy calls == use
        if use == 0:
            # graduation review, softened (direction C / Hermes "absence of evidence"): a viewed
            # symbol had recall value even without a Skill invocation — only use AND view both
            # zero is genuine dormancy. The suspend gate parks the review entirely while the
            # recall surface is known-broken (archiving for zero use would bury surfacing's failure).
            if not review_suspended and m.get("view", 0) == 0:
                archive.add(m["name"])
            continue  # spared zero-use symbols stay out of the pool either way
        survivors.append((_rate(use, denom), m["name"]))
    if len(survivors) > capacity:
        survivors.sort(key=lambda rn: (rn[0], hashlib.md5(rn[1].encode()).digest()))  # rate then deterministic hash
        archive.update(name for _, name in survivors[: len(survivors) - capacity])
    return sorted(archive)
