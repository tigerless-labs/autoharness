from autoharness.lib import lifecycle


def _m(name, calls, anchor=0):
    return {"name": name, "calls": calls, "anchor": anchor}


def test_probation_never_archived():
    # denom = 5 - 0 = 5 < maturity 10 → probation, even with zero calls
    out = lifecycle.evaluate([_m("new", 0)], request_count=5, maturity=10, capacity=1)
    assert out == []


def test_mature_zero_calls_survives_without_capacity_pressure():
    # denom = 20 ≥ maturity 10, calls 0, pool under cap → capacity contention is the only death
    out = lifecycle.evaluate([_m("idle", 0)], request_count=20, maturity=10, capacity=5)
    assert out == []


def test_mature_zero_calls_evicted_first_under_capacity_pressure():
    members = [_m("idle", 0), _m("used", 30)]
    out = lifecycle.evaluate(members, request_count=100, maturity=10, capacity=1)
    assert out == ["idle"]


def test_capacity_competition_archives_lowest_rate():
    members = [_m("hi", 80), _m("mid", 40), _m("lo", 5)]  # denom 100 each, rates .8/.4/.05
    out = lifecycle.evaluate(members, request_count=100, maturity=10, capacity=2)
    assert out == ["lo"]  # only the weakest of the mature pool, kept down to capacity


def test_high_rate_kept_under_capacity():
    members = [_m("a", 50), _m("b", 90)]
    out = lifecycle.evaluate(members, request_count=100, maturity=10, capacity=5)
    assert out == []  # under capacity → nobody archived


def test_denominator_grows_with_requests():
    # same symbol: probation at low request count, joins the mature pool once denom passes maturity
    m = [_m("x", 0, anchor=0), _m("y", 8, anchor=0)]
    assert lifecycle.evaluate(m, request_count=9, maturity=10, capacity=1) == []       # denom 9 < 10: both probation
    assert lifecycle.evaluate(m, request_count=10, maturity=10, capacity=1) == ["x"]   # mature pool of 2 over cap 1, lowest rate out


def test_anchor_offsets_denominator():
    # created late (anchor 95): denom = 100 - 95 = 5 < maturity → still probation
    out = lifecycle.evaluate([_m("late", 0, anchor=95)], request_count=100, maturity=10, capacity=1)
    assert out == []


def test_capacity_tiebreak_by_name_deterministic():
    # equal rates, capacity forces one out → lexicographically-first name archived
    members = [_m("b", 10), _m("a", 10), _m("c", 10)]  # all rate .1
    out = lifecycle.evaluate(members, request_count=100, maturity=10, capacity=2)
    assert out == ["a"]


def test_probation_does_not_count_toward_capacity():
    # one mature survivor + two probation; capacity 1 not breached by probation members
    members = [_m("mature", 50, anchor=0), _m("p1", 0, anchor=95), _m("p2", 0, anchor=96)]
    out = lifecycle.evaluate(members, request_count=100, maturity=10, capacity=1)
    assert out == []  # probation excluded from the mature pool, no capacity pressure
