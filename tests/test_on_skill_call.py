import pytest

from autoharness import config
from autoharness.hook import on_skill_call
from autoharness.lib import sidecar, skill_store


@pytest.fixture(autouse=True)
def _unguard(monkeypatch):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)  # ambient may set it


def _roots(tmp_path):
    return {"global": tmp_path / "g", "project": tmp_path / "p"}


def _seed_agent_skill(roots, name="foo"):
    root = roots["project"]
    skill_store.write_body("project", name, "b", root)
    sidecar.create("project", name, anchor=0, root=root)
    return root


def test_agent_created_call_bumps_numerator(tmp_path):
    roots = _roots(tmp_path)
    root = _seed_agent_skill(roots)
    r = on_skill_call.on_skill_call({"skill_name": "foo"}, roots=roots)
    assert r["counted"] and r["level"] == "project"
    assert sidecar.read("project", "foo", root)["calls"] == 1


def test_nested_tool_input_name(tmp_path):
    roots = _roots(tmp_path)
    _seed_agent_skill(roots)
    r = on_skill_call.on_skill_call({"tool_input": {"name": "foo"}}, roots=roots)
    assert r["counted"]


def test_native_or_user_skill_never_touched(tmp_path):
    # present in tree but NOT agent-created → zero-intrusion: no sidecar write at all
    roots = _roots(tmp_path)
    root = roots["project"]
    skill_store.write_body("project", "native", "b", root)
    r = on_skill_call.on_skill_call({"skill_name": "native"}, roots=roots)
    assert not r["counted"] and r["reason"] == "not_agent_created"
    assert sidecar.read("project", "native", root) == {}  # untouched host artifact


def test_unknown_symbol_failsafe(tmp_path):
    r = on_skill_call.on_skill_call({"skill_name": "ghost"}, roots=_roots(tmp_path))
    assert not r["counted"]


def test_missing_name_failsafe(tmp_path):
    assert not on_skill_call.on_skill_call({}, roots=_roots(tmp_path))["counted"]


def test_recursion_guard_does_not_count(tmp_path, monkeypatch):
    monkeypatch.setenv(config.CHILD_SESSION_ENV, "1")
    roots = _roots(tmp_path)
    root = _seed_agent_skill(roots)
    r = on_skill_call.on_skill_call({"skill_name": "foo"}, roots=roots)
    assert not r["counted"] and r["reason"] == "recursion_guard"
    assert sidecar.read("project", "foo", root)["calls"] == 0  # reflector's own calls excluded


def test_platform_child_var_does_not_gate_counting(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", "1")  # host sets this on every hook subprocess, not just reflectors
    roots = _roots(tmp_path)
    root = _seed_agent_skill(roots)
    r = on_skill_call.on_skill_call({"skill_name": "foo"}, roots=roots)
    assert r["counted"] and sidecar.read("project", "foo", root)["calls"] == 1
