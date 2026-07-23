from pathlib import Path

from autoharness import config
from autoharness.hook import spawn
from autoharness.lib import counters, layer, ledger, sidecar, skill_store

_SRC = str(Path(__file__).resolve().parents[1] / "src")

GOOD = "---\nname: {n}\ndescription: {d}\n---\n# {n}\nbody\n"


def _roots(tmp_path):
    return {"global": tmp_path / "g", "project": tmp_path / "p"}


def test_main_parses_argv_and_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(spawn.capture, "window", lambda tp, off, **k: (f"WIN[{tp}|{off}]", 42))
    monkeypatch.setattr(spawn.capture, "digest", lambda tp, off, **k: f"DIG[{tp}|{off}]")
    seen = {}
    monkeypatch.setattr(spawn, "run",
                        lambda w, rid, **k: seen.update(w=w, rid=rid, roots=k["roots"], digest=k["digest"]))
    spawn.main(["/t.jsonl", "sess-1", "run-9", str(tmp_path / "p"), str(tmp_path / "g")])
    assert seen["w"] == "WIN[/t.jsonl|0]"
    assert seen["digest"] == "DIG[/t.jsonl|0]"  # digest covers the bytes before the window offset
    assert seen["rid"] == "run-9"
    assert seen["roots"][layer.PROJECT] == tmp_path / "p"
    assert seen["roots"][layer.GLOBAL] == tmp_path / "g"
    assert counters.session_offset("sess-1", tmp_path / "p") == 42


def test_main_offset_advances_only_after_run(tmp_path, monkeypatch):
    monkeypatch.setattr(spawn.capture, "window", lambda tp, off, **k: ("W", 99))
    monkeypatch.setattr(spawn.capture, "digest", lambda tp, off, **k: "")
    monkeypatch.setattr(spawn, "run", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    counters.write_session_offset("sess-2", 7, tmp_path / "p")
    try:
        spawn.main(["/t.jsonl", "sess-2", "run-1", str(tmp_path / "p"), str(tmp_path / "g")])
    except RuntimeError:
        pass
    assert counters.session_offset("sess-2", tmp_path / "p") == 7  # crash -> window re-fed next time


# --- U3 deterministic assembly ---

def test_description_index_both_layers_skip_archive(tmp_path):
    roots = _roots(tmp_path)
    skill_store.write_body("global", "g1", GOOD.format(n="g1", d="global one"), roots["global"])
    skill_store.write_body("project", "p1", GOOD.format(n="p1", d="proj one"), roots["project"])
    skill_store.write_body("project", "p1", GOOD.format(n="p1", d="proj one"), roots["project"])
    skill_store.archive("project", "p1", roots["project"])  # p1 now archived → must vanish
    skill_store.write_body("project", "p2", GOOD.format(n="p2", d="proj two"), roots["project"])

    idx = spawn.description_index(roots)
    assert "g1" in idx and "global one" in idx
    assert "p2" in idx and "proj two" in idx
    assert "global" in idx and "project" in idx
    assert "p1" not in idx  # archived skill never offered to compare-first


def test_description_index_empty_is_placeholder(tmp_path):
    idx = spawn.description_index(_roots(tmp_path))
    assert idx.strip()  # non-empty, no crash on empty trees


def test_build_bundle_injects_three_pieces():
    b = spawn.build_bundle("WINDOW_MARK", "INDEX_MARK", "SPEC_MARK")
    assert "WINDOW_MARK" in b and "INDEX_MARK" in b and "SPEC_MARK" in b


def test_build_bundle_prepends_digest_when_present():
    b = spawn.build_bundle("WINDOW_MARK", "INDEX_MARK", "SPEC_MARK", digest="DIGEST_MARK")
    assert "DIGEST_MARK" in b
    assert b.index("DIGEST_MARK") < b.index("WINDOW_MARK")  # chronological: prior context first
    assert "DIGEST_MARK" not in spawn.build_bundle("W", "I", "S", digest="")  # empty -> no section


def test_build_command_carries_agent_and_print():
    cmd = spawn.build_command(agent="autoharness:reflector", claude_bin="claude")
    assert cmd[0] == "claude"
    assert "--agent" in cmd and "autoharness:reflector" in cmd
    assert "-p" in cmd
    # autonomous spawn: no human to approve tool calls → must skip permission prompts
    assert "--dangerously-skip-permissions" in cmd


def test_child_env_sets_guard_and_coords_without_polluting():
    base = {"PATH": "/x"}
    env = spawn.child_env("run-1", Path("/repo"), base_env=base)
    assert env[config.CHILD_SESSION_ENV]
    assert env[config.RUN_ID_ENV] == "run-1"
    assert env[config.PROJECT_ROOT_ENV] == "/repo"
    assert env["PATH"] == "/x"
    assert base == {"PATH": "/x"}  # input dict untouched (no parent pollution)


# --- U4 run orchestration + system (fake reflector) ---

def test_run_feeds_bundle_and_drains_no_handoff_persisted(tmp_path):
    roots = _roots(tmp_path)
    seen = {}

    def fake_spawn(argv, env, bundle):
        seen["env"] = env
        seen["bundle"] = bundle
        # stand in for the reflector: emit one canned intent into the run's queue
        from autoharness.lib import intent_queue
        intent_queue.append(env[config.RUN_ID_ENV],
                            {"action": "create", "name": "learned", "level": "project",
                             "body": GOOD.format(n="learned", d="a specific thing"),
                             "reason": "compare-first new", "evidence": "window slice"},
                            roots["project"])

    verdicts = spawn.run("WINDOW", "run-x", roots=roots, spec_path=config.FORMAT_SPEC,
                         spawn_fn=fake_spawn)
    assert seen["env"][config.RUN_ID_ENV] == "run-x"
    assert "WINDOW" in seen["bundle"]
    assert [v["ok"] for v in verdicts] == [True]
    assert skill_store.read_body("project", "learned", roots["project"]) is not None
    assert not (layer.state_dir(layer.PROJECT, roots["project"]) / "handoff").exists()  # bundle lives only in the pipe


# --- curator: periodic consolidation pass (reuses the reflector spawn chain) ---

def test_description_index_agent_only_filters_native(tmp_path):
    roots = _roots(tmp_path)
    skill_store.write_body("project", "native1", GOOD.format(n="native1", d="native"), roots["project"])
    skill_store.write_body("project", "agent1", GOOD.format(n="agent1", d="agent made"), roots["project"])
    sidecar.create("project", "agent1", 0, roots["project"])  # created_by:agent
    idx = spawn.description_index(roots, agent_only=True)
    assert "agent1" in idx
    assert "native1" not in idx  # the curator only ever sees its own skills


def test_curator_bundle_has_index_and_spec():
    b = spawn.build_curator_bundle("INDEX_MARK", "SPEC_MARK")
    assert "INDEX_MARK" in b and "SPEC_MARK" in b


def test_curate_main_parses_argv_and_runs(tmp_path, monkeypatch):
    seen = {}
    monkeypatch.setattr(spawn, "run_curator",
                        lambda rid, **k: seen.update(rid=rid, roots=k["roots"]))
    spawn.main(["--curate", "run-c9", str(tmp_path / "p"), str(tmp_path / "g")])
    assert seen["rid"] == "run-c9"
    assert seen["roots"][layer.PROJECT] == tmp_path / "p"
    assert seen["roots"][layer.GLOBAL] == tmp_path / "g"


def test_run_curator_lands_merge_and_archives_narrow(tmp_path):
    roots = _roots(tmp_path)
    root = roots["project"]
    skill_store.write_body("project", "widgets", GOOD.format(n="widgets", d="widget umbrella"), root)
    sidecar.create("project", "widgets", 0, root)
    skill_store.write_body("project", "widget-delta", GOOD.format(n="widget-delta", d="narrow delta"), root)
    sidecar.create("project", "widget-delta", 0, root)

    def fake_curator(argv, env, bundle):
        from autoharness.lib import intent_queue
        rid = env[config.RUN_ID_ENV]
        intent_queue.append(rid, {"action": "patch", "name": "widgets",
                                  "old_string": "body", "new_string": "body\n## delta\nabsorbed",
                                  "reason": "fold widget-delta into the widgets umbrella",
                                  "evidence": "widgets [project] / widget-delta [project]"}, root)
        intent_queue.append(rid, {"action": "delete", "name": "widget-delta",
                                  "reason": "absorbed into widgets umbrella",
                                  "evidence": "widgets [project] / widget-delta [project]"}, root)

    verdicts = spawn.run_curator("run-c", roots=roots, spec_path=config.FORMAT_SPEC, spawn_fn=fake_curator)
    assert [v["ok"] for v in verdicts] == [True, True]
    assert "absorbed" in skill_store.read_body("project", "widgets", root)
    assert skill_store.read_body("project", "widget-delta", root) is None  # moved out of the live tree
    assert (layer.archive_dir("project", root) / "widget-delta").exists()  # archive is recoverable
    assert any(e["action"] == "patch" for e in ledger.read("project", "widgets", root))


def test_run_curator_cannot_touch_native_skill(tmp_path):
    # red team: the shared promoter membership guard rejects any modify on a non-agent skill
    roots = _roots(tmp_path)
    root = roots["project"]
    skill_store.write_body("project", "native", GOOD.format(n="native", d="native"), root)  # no sidecar

    def fake_curator(argv, env, bundle):
        from autoharness.lib import intent_queue
        intent_queue.append(env[config.RUN_ID_ENV],
                            {"action": "delete", "name": "native",
                             "reason": "tried to prune a native skill", "evidence": "native [project]"}, root)

    verdicts = spawn.run_curator("run-r", roots=roots, spec_path=config.FORMAT_SPEC, spawn_fn=fake_curator)
    assert verdicts and verdicts[0]["ok"] is False
    assert "self_produced" in str(verdicts[0]["findings"])
    assert skill_store.read_body("project", "native", root) is not None  # native untouched


def _fake_reflector_script(tmp_path):
    script = tmp_path / "fake_reflector.py"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "from pathlib import Path\n"
        "from autoharness import config\n"
        "from autoharness.stage_skill import server\n"
        "sys.stdin.read()\n"  # consume the handoff bundle (proves it arrived on stdin)
        "run_id = os.environ[config.RUN_ID_ENV]\n"
        "root = Path(os.environ[config.PROJECT_ROOT_ENV])\n"
        "params = {'action': 'create', 'name': 'learned', 'level': 'project',\n"
        "          'body': '---\\nname: learned\\ndescription: Does a specific thing.\\n---\\n# x\\ny\\n',\n"
        "          'reason': 'compare-first new', 'evidence': 'window slice'}\n"
        "res = server.stage(params, run_id=run_id, root=root)\n"
        "sys.exit(0 if res['ok'] else 1)\n"
    )
    script.chmod(0o755)
    return script


def test_system_fake_reflector_cross_process_lands(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", _SRC)  # child subprocess must import autoharness
    roots = _roots(tmp_path)
    script = _fake_reflector_script(tmp_path)

    verdicts = spawn.run("WINDOW", "run-sys", roots=roots, repo_name="myrepo",
                         claude_bin=str(script), spec_path=config.FORMAT_SPEC)

    assert [v["ok"] for v in verdicts] == [True]
    root = roots["project"]
    assert skill_store.read_body("project", "learned", root) is not None
    assert sidecar.is_agent_created("project", "learned", root)
    led = ledger.read("project", "learned", root)
    assert len(led) == 1 and led[0]["action"] == "create"


def _fake_curator_script(tmp_path):
    script = tmp_path / "fake_curator.py"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import os, sys\n"
        "from pathlib import Path\n"
        "from autoharness import config\n"
        "from autoharness.stage_skill import server\n"
        "sys.stdin.read()\n"  # consume the curator bundle (proves it arrived on stdin)
        "run_id = os.environ[config.RUN_ID_ENV]\n"
        "root = Path(os.environ[config.PROJECT_ROOT_ENV])\n"
        "ev = 'widgets [project] / widget-delta [project]'\n"
        "server.stage({'action': 'patch', 'name': 'widgets', 'old_string': 'body',\n"
        "              'new_string': 'body\\n## delta\\nabsorbed', 'reason': 'fold into umbrella',\n"
        "              'evidence': ev}, run_id=run_id, root=root)\n"
        "server.stage({'action': 'delete', 'name': 'widget-delta',\n"
        "              'reason': 'absorbed into widgets', 'evidence': ev}, run_id=run_id, root=root)\n"
        "sys.exit(0)\n"
    )
    script.chmod(0o755)
    return script


def test_system_fake_curator_cross_process_merges(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", _SRC)  # child subprocess must import autoharness
    roots = _roots(tmp_path)
    root = roots["project"]
    for n, d in (("widgets", "widget umbrella"), ("widget-delta", "narrow delta")):
        skill_store.write_body("project", n, GOOD.format(n=n, d=d), root)
        sidecar.create("project", n, 0, root)
    script = _fake_curator_script(tmp_path)

    verdicts = spawn.run_curator("run-csys", roots=roots, repo_name="myrepo",
                                 claude_bin=str(script), spec_path=config.FORMAT_SPEC)

    assert [v["ok"] for v in verdicts] == [True, True]
    assert "absorbed" in skill_store.read_body("project", "widgets", root)
    assert skill_store.read_body("project", "widget-delta", root) is None  # archived out of the live tree
    assert (layer.archive_dir("project", root) / "widget-delta").exists()
