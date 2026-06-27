from autoharness import config
from autoharness.hook import on_stop
from autoharness.lib import counters

EV = {"session_id": "sess-1"}


def _unguard(monkeypatch):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)


def test_each_stop_increments_no_trigger(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    for expected in (1, 2, 3):
        v = on_stop.on_stop(EV, root=tmp_path, n=10)
        assert not v["triggered"] and v["count"] == expected


def test_triggers_and_resets_at_n(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    on_stop.on_stop(EV, root=tmp_path, n=3)
    on_stop.on_stop(EV, root=tmp_path, n=3)
    v = on_stop.on_stop(EV, root=tmp_path, n=3)
    assert v["triggered"] and v["window_n"] == 3
    assert counters.session_count("sess-1", tmp_path) == 0  # reset on trigger
    assert on_stop.on_stop(EV, root=tmp_path, n=3)["count"] == 1  # next round starts at 1


def test_recursion_guard_early_exit_no_count(monkeypatch, tmp_path):
    monkeypatch.setenv(config.CHILD_SESSION_ENV, "reflector-xyz")
    v = on_stop.on_stop(EV, root=tmp_path, n=3)
    assert not v["triggered"]
    assert counters.session_count("sess-1", tmp_path) == 0  # child Stop does not count


def test_missing_session_safe(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    assert not on_stop.on_stop({}, root=tmp_path, n=3)["triggered"]
