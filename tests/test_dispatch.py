from pathlib import Path

import pytest

from autoharness import config
from autoharness.hook import dispatch
from autoharness.lib import counters, layer, sidecar, skill_store


@pytest.fixture(autouse=True)
def _unguard(monkeypatch):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)  # ambient may set it


def _roots(tmp_path):
    return {layer.GLOBAL: tmp_path / "g", layer.PROJECT: tmp_path / "p"}


def test_routes_each_event_to_its_handler(tmp_path, monkeypatch):
    seen = {}

    def spy(key, ret):
        def fake(e, **k):
            seen[key] = (e, k)
            return ret
        return fake

    monkeypatch.setattr(dispatch.on_session_start, "on_session_start", spy("start", {"archived": {}}))
    monkeypatch.setattr(dispatch.on_skill_call, "on_skill_call", spy("skill", {"counted": False}))
    monkeypatch.setattr(dispatch.on_stop, "on_stop", spy("stop", {"triggered": False}))
    monkeypatch.setattr(dispatch.on_session_end, "on_session_end", spy("end", {"triggered": False}))
    roots = _roots(tmp_path)

    dispatch.dispatch({"hook_event_name": "SessionStart"}, roots=roots)
    dispatch.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Skill"}, roots=roots)
    dispatch.dispatch({"hook_event_name": "Stop"}, roots=roots)
    dispatch.dispatch({"hook_event_name": "SessionEnd"}, roots=roots)

    assert set(seen) == {"start", "skill", "stop", "end"}
    assert seen["stop"][1]["root"] == roots[layer.PROJECT]
    assert seen["skill"][1]["roots"] == roots


def test_unknown_event_is_ignored_safely(tmp_path):
    assert dispatch.dispatch({"hook_event_name": "Nope"}, roots=_roots(tmp_path))["ignored"] is True


def test_missing_event_name_is_ignored(tmp_path):
    assert dispatch.dispatch({}, roots=_roots(tmp_path))["ignored"] is True


def test_subagent_stop_is_ignored(tmp_path):
    # reflector completion is SubagentStop (E6 S4): never a turn, never counted
    assert dispatch.dispatch({"hook_event_name": "SubagentStop"}, roots=_roots(tmp_path))["ignored"] is True


def test_child_session_stop_bumps_nothing(tmp_path, monkeypatch):
    # a reflector child's turns must not inflate MNG denominators (guard runs before the bump)
    monkeypatch.setenv(config.CHILD_SESSION_ENV, "1")
    roots = _roots(tmp_path)
    out = dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s1"},
                            roots=roots, reflect=lambda *a: None)
    assert out["result"]["triggered"] is False
    assert counters.request_count(layer.PROJECT, roots[layer.PROJECT]) == 0
    assert counters.request_count(layer.GLOBAL, roots[layer.GLOBAL]) == 0


def test_stop_bumps_both_layer_denominators(tmp_path):
    roots = _roots(tmp_path)
    dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s1"},
                      roots=roots, reflect=lambda *a: None)
    assert counters.request_count(layer.PROJECT, roots[layer.PROJECT]) == 1
    assert counters.request_count(layer.GLOBAL, roots[layer.GLOBAL]) == 1  # global denominator too


def test_triggered_stop_fires_reflect(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatch.on_stop, "on_stop",
                        lambda e, **k: {"triggered": True, "session_id": "s1", "count": 10, "window_n": 10})
    calls = []
    dispatch.dispatch({"hook_event_name": "Stop", "transcript_path": "/t.jsonl"},
                      roots=_roots(tmp_path), reflect=lambda ev, res, roots: calls.append(res))
    assert calls and calls[0]["session_id"] == "s1"


def test_real_onstop_triggers_at_cadence(tmp_path):
    roots = _roots(tmp_path)
    for _ in range(config.REFLECT_EVERY_N - 1):
        counters.bump_session("s1", roots[layer.PROJECT])
    seen = []
    dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s1", "transcript_path": "/t.jsonl"},
                      roots=roots, reflect=lambda ev, res, roots: seen.append(res))
    assert len(seen) == 1 and seen[0]["window_n"] == config.REFLECT_EVERY_N


def test_curate_run_id_sanitized_and_unique_per_count():
    assert dispatch._curate_run_id({"session_id": "abc/1"}, 5) == "abc1-c5"


def test_curator_fires_at_consolidate_cadence(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatch.config, "CONSOLIDATE_EVERY_N", 3)
    roots = _roots(tmp_path)
    fired = []
    for _ in range(3):
        dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s1", "transcript_path": "/t.jsonl"},
                          roots=roots, reflect=lambda *a: None,
                          consolidate=lambda run_id, r: fired.append(run_id))
    assert fired == ["s1-c3"]  # once, on the turn the request counter hits a multiple of N


def test_curator_not_fired_off_cadence(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatch.config, "CONSOLIDATE_EVERY_N", 3)
    roots = _roots(tmp_path)
    fired = []
    for _ in range(2):
        dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s1"},
                          roots=roots, reflect=lambda *a: None,
                          consolidate=lambda run_id, r: fired.append(run_id))
    assert fired == []


def test_curator_not_fired_in_child_session(tmp_path, monkeypatch):
    monkeypatch.setenv(config.CHILD_SESSION_ENV, "1")
    monkeypatch.setattr(dispatch.config, "CONSOLIDATE_EVERY_N", 1)  # would fire every turn if unguarded
    fired = []
    dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s1"}, roots=_roots(tmp_path),
                      reflect=lambda *a: None, consolidate=lambda run_id, r: fired.append(run_id))
    assert fired == []  # recursion guard: a curator/reflector child never spawns another curator


def test_untriggered_stop_does_not_reflect(tmp_path, monkeypatch):
    monkeypatch.setattr(dispatch.on_stop, "on_stop", lambda e, **k: {"triggered": False, "count": 1})
    calls = []
    dispatch.dispatch({"hook_event_name": "Stop"}, roots=_roots(tmp_path),
                      reflect=lambda ev, res, roots: calls.append(res))
    assert calls == []


def test_pretooluse_skill_counts_numerator(tmp_path):
    roots = _roots(tmp_path)
    root = roots[layer.PROJECT]
    skill_store.write_body("project", "foo", "b", root)
    sidecar.create("project", "foo", anchor=0, root=root)
    out = dispatch.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Skill",
                             "tool_input": {"name": "foo"}}, roots=roots)
    assert out["result"]["counted"]
    assert sidecar.read("project", "foo", root)["calls"] == 1


def test_pretooluse_read_of_skill_counts_numerator(tmp_path):
    roots = _roots(tmp_path)
    root = roots[layer.PROJECT]
    skill_store.write_body("project", "foo", "b", root)
    sidecar.create("project", "foo", anchor=0, root=root)
    out = dispatch.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Read",
                             "tool_input": {"file_path": str(root / "skills" / "foo" / "SKILL.md")}},
                            roots=roots)
    assert out["result"]["counted"]
    assert sidecar.read("project", "foo", root)["calls"] == 1


def test_reflector_read_not_counted(tmp_path):
    roots = _roots(tmp_path)
    root = roots[layer.PROJECT]
    skill_store.write_body("project", "foo", "b", root)
    sidecar.create("project", "foo", anchor=0, root=root)
    out = dispatch.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Read",
                             "agent_type": "autoharness:reflector",
                             "tool_input": {"file_path": str(root / "skills" / "foo" / "SKILL.md")}},
                            roots=roots)
    assert not out["result"]["counted"]
    assert sidecar.read("project", "foo", root)["calls"] == 0


def test_reflector_write_is_denied(tmp_path):
    out = dispatch.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Write",
                             "agent_type": "autoharness:reflector"}, roots=_roots(tmp_path))
    assert out["deny"] is True


def test_non_reflector_write_is_ignored(tmp_path):
    out = dispatch.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Write",
                             "agent_type": "main"}, roots=_roots(tmp_path))
    assert out["ignored"] is True


def test_handler_exception_is_failsafe(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr(dispatch.counters, "bump_request", boom)
    out = dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s1"}, roots=_roots(tmp_path))
    assert "error" in out  # never propagates to crash the host hook


def test_reflect_builds_run_id_and_skips_without_transcript(tmp_path):
    launched = []
    result = {"session_id": "abc", "count": 7, "window_n": 7}
    dispatch._reflect({"transcript_path": "/t.jsonl"}, result, _roots(tmp_path),
                      launch=lambda tp, sid, run_id, roots: launched.append((tp, sid, run_id)))
    assert launched == [("/t.jsonl", "abc", "abc-7")]

    launched.clear()
    dispatch._reflect({}, result, _roots(tmp_path), launch=lambda *a: launched.append(a))
    assert launched == []  # no transcript → nothing to reflect on


def test_default_roots_resolve_both_layers():
    roots = dispatch._roots(None)
    assert set(roots) == set(layer.LAYERS)
    assert all(isinstance(p, Path) for p in roots.values())
