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
    seen = {}
    monkeypatch.setattr(spawn, "run",
                        lambda w, rid, **k: seen.update(w=w, rid=rid, roots=k["roots"]))
    spawn.main(["/t.jsonl", "sess-1", "run-9", str(tmp_path / "p"), str(tmp_path / "g")])
    assert seen["w"] == "WIN[/t.jsonl|0]"
    assert seen["rid"] == "run-9"
    assert seen["roots"][layer.PROJECT] == tmp_path / "p"
    assert seen["roots"][layer.GLOBAL] == tmp_path / "g"
    assert counters.session_offset("sess-1", tmp_path / "p") == 42


def test_main_offset_advances_only_after_run(tmp_path, monkeypatch):
    monkeypatch.setattr(spawn.capture, "window", lambda tp, off, **k: ("W", 99))
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

def test_run_materializes_handoff_and_drains(tmp_path):
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
