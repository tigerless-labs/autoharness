from autoharness import config
from autoharness.hook import on_session_end
from autoharness.lib import counters

EV = {"session_id": "sess-1"}


def _unguard(monkeypatch):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)


def test_flush_remaining_window_equals_count(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    counters.bump_session("sess-1", tmp_path)
    counters.bump_session("sess-1", tmp_path)
    counters.bump_session("sess-1", tmp_path)  # tail below threshold = 3
    v = on_session_end.on_session_end(EV, root=tmp_path)
    assert v["triggered"] and v["window_n"] == 3  # current count tells REF how many to feed


def test_self_deletes_counter(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    counters.bump_session("sess-1", tmp_path)
    p = counters._session_path("sess-1", tmp_path)
    assert p.exists()
    on_session_end.on_session_end(EV, root=tmp_path)
    assert not p.exists()  # self-deletes on teardown


def test_no_flush_when_zero(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    v = on_session_end.on_session_end(EV, root=tmp_path)
    assert not v["triggered"]


def test_recursion_guard_no_flush(monkeypatch, tmp_path):
    monkeypatch.setenv(config.CHILD_SESSION_ENV, "reflector-xyz")
    counters.bump_session("sess-1", tmp_path)
    v = on_session_end.on_session_end(EV, root=tmp_path)
    assert not v["triggered"]


def test_platform_child_var_does_not_gate_flush(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", "1")  # host sets this on every hook subprocess, not just reflectors
    counters.bump_session("sess-1", tmp_path)
    assert on_session_end.on_session_end(EV, root=tmp_path)["triggered"]
