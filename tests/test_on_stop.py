from autoharness import config
from autoharness.hook import on_stop
from autoharness.lib import counters

EV = {"session_id": "sess-1"}


def _unguard(monkeypatch):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)


def test_stop_reads_activity_without_advancing(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    counters.bump_session("sess-1", tmp_path)
    for _ in range(3):
        v = on_stop.on_stop(EV, root=tmp_path, n=10)
        assert not v["triggered"] and v["count"] == 1  # Stop judges, never advances


def test_triggers_and_resets_at_n(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    for _ in range(3):
        counters.bump_session("sess-1", tmp_path)
    v = on_stop.on_stop(EV, root=tmp_path, n=3)
    assert v["triggered"] and v["window_n"] == 3
    assert counters.session_count("sess-1", tmp_path) == 0  # reset on trigger
    assert not on_stop.on_stop(EV, root=tmp_path, n=3)["triggered"]  # next round starts empty


def test_recursion_guard_early_exit_no_count(monkeypatch, tmp_path):
    monkeypatch.setenv(config.CHILD_SESSION_ENV, "reflector-xyz")
    v = on_stop.on_stop(EV, root=tmp_path, n=3)
    assert not v["triggered"]
    assert counters.session_count("sess-1", tmp_path) == 0  # child Stop does not count


def test_platform_child_var_does_not_gate_judging(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", "1")  # host sets this on every hook subprocess, not just reflectors
    counters.bump_session("sess-1", tmp_path)
    assert on_stop.on_stop(EV, root=tmp_path, n=10).get("count") == 1


def test_missing_session_safe(monkeypatch, tmp_path):
    _unguard(monkeypatch)
    assert not on_stop.on_stop({}, root=tmp_path, n=3)["triggered"]


# --- activity-quantum trigger (hermes-parity Phase 11, direction H): the numerator is tool calls,
# accumulated by PreToolUse; Stop only judges the threshold. Chat-only turns never advance it. ---

def test_stop_without_activity_never_triggers(tmp_path):
    for _ in range(50):
        r = on_stop.on_stop({"session_id": "s1"}, root=tmp_path, n=3)
    assert not r["triggered"]  # pure-chat turns: counter untouched


def test_tool_calls_accumulate_and_stop_judges(tmp_path):
    from autoharness.lib import counters
    for _ in range(3):
        counters.bump_session("s1", tmp_path)  # what dispatch does per PreToolUse now
    r = on_stop.on_stop({"session_id": "s1"}, root=tmp_path, n=3)
    assert r["triggered"] and r["count"] == 3
    # reset after firing
    assert counters.session_count("s1", tmp_path) == 0
