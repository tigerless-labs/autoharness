"""Project-only deployments must leave the global layer untouched (#191)."""

import importlib

import pytest

from autoharness import config
from autoharness.hook import dispatch, on_session_start, on_skill_call, promoter, spawn
from autoharness.lib import counters, intent_queue, layer, metrics, sidecar, skill_store
from autoharness.stage_skill import server

BODY = "---\nname: foo\ndescription: Use when formatting a date.\n---\nUse strftime.\n"


def _create(level):
    return {"action": "create", "name": "foo", "body": BODY, "level": level,
            "reason": "repeat", "evidence": "synthetic evidence"}


def _snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes()
            for p in root.rglob("*") if p.is_file()} if root.exists() else {}


@pytest.fixture
def roots(tmp_path):
    return {layer.GLOBAL: tmp_path / "global", layer.PROJECT: tmp_path / "project"}


@pytest.fixture
def project_only(monkeypatch):
    monkeypatch.setattr(config, "DISABLE_GLOBAL", True, raising=False)


def test_disable_global_reads_environment(monkeypatch):
    monkeypatch.setenv("AUTOHARNESS_DISABLE_GLOBAL", "1")
    importlib.reload(config)
    try:
        assert getattr(config, "DISABLE_GLOBAL", False) is True
    finally:
        monkeypatch.undo()
        importlib.reload(config)


def test_stage_rejects_global_without_appending(roots, project_only):
    result = server.stage(_create(layer.GLOBAL), run_id="run1", root=roots[layer.PROJECT])
    assert not result["ok"]
    assert any("disabled" in str(error) for error in result["errors"])
    assert intent_queue.read("run1", roots[layer.PROJECT]) == []


def test_promoter_rejects_global_and_keeps_project_working(roots, project_only):
    result = promoter.promote(_create(layer.GLOBAL), roots=roots)
    assert not result["ok"]
    assert not roots[layer.GLOBAL].exists()
    assert promoter.promote(_create(layer.PROJECT), roots=roots)["ok"]
    assert skill_store.exists(layer.PROJECT, "foo", roots[layer.PROJECT])


def test_stop_never_creates_global_counter_or_sweeps_global_files(roots, project_only):
    global_skills = layer.skills_dir(layer.GLOBAL, roots[layer.GLOBAL])
    global_skills.mkdir(parents=True)
    (global_skills / "pending.tmp").write_text("other deployment's temporary file")
    before = _snapshot(roots[layer.GLOBAL])

    result = dispatch.dispatch({"hook_event_name": "Stop", "session_id": "s"}, roots=roots)

    assert "error" not in result
    assert counters.request_count(layer.PROJECT, roots[layer.PROJECT]) == 1
    assert _snapshot(roots[layer.GLOBAL]) == before


def test_existing_global_skill_is_neither_archived_recalled_nor_counted(roots, monkeypatch):
    assert promoter.promote(_create(layer.GLOBAL), roots=roots)["ok"]
    counters.bump_request(layer.GLOBAL, roots[layer.GLOBAL])
    before = _snapshot(roots[layer.GLOBAL])
    monkeypatch.setattr(config, "DISABLE_GLOBAL", True, raising=False)
    monkeypatch.setattr(config, "MATURITY_THRESHOLD", {layer.GLOBAL: 0, layer.PROJECT: 0})

    started = on_session_start.on_session_start(roots=roots)
    assert not started["archived"].get(layer.GLOBAL)
    assert not started["context"]
    assert spawn.description_index(roots) == "(no live skills yet)"
    assert set(metrics.collect(roots)) == {layer.PROJECT}
    assert not on_skill_call.on_skill_call({"skill_name": "foo"}, roots=roots)["counted"]
    path = skill_store.skill_path(layer.GLOBAL, "foo", roots[layer.GLOBAL])
    assert not on_skill_call.on_skill_read({"file_path": str(path)}, roots=roots)["counted"]
    assert not promoter.promote({"action": "delete", "name": "foo",
                                 "reason": "r", "evidence": "e"}, roots=roots)["ok"]
    spawn._snapshot_skills("curator1", roots)
    snapshots = layer.state_dir(layer.PROJECT, roots[layer.PROJECT]) / "snapshots"
    assert not list(snapshots.glob("*-global.tar.gz"))
    assert _snapshot(roots[layer.GLOBAL]) == before


def test_global_names_do_not_block_project_skill_resolution(roots, monkeypatch):
    # namesakes in both layers (a create refuses to make them, but a user or an older version can):
    # with global disabled, the project one is the one that resolves and counts
    for lyr in layer.LAYERS:
        skill_store.write_body(lyr, "foo", _create(lyr)["body"], roots[lyr])
        sidecar.create(lyr, "foo", 0, roots[lyr])
    monkeypatch.setattr(config, "DISABLE_GLOBAL", True, raising=False)

    assert on_skill_call.on_skill_call({"skill_name": "foo"}, roots=roots)["level"] == layer.PROJECT
    assert sidecar.read(layer.PROJECT, "foo", roots[layer.PROJECT])["use"] == 1
    assert sidecar.read(layer.GLOBAL, "foo", roots[layer.GLOBAL])["use"] == 0
