"""Real detached-process and SessionStart controls; no live model calls."""
import json
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from autoharness import config
from autoharness.hook import on_session_start, promoter
from autoharness.lib import intent_queue, layer, skill_store

pytestmark = pytest.mark.skipif(not hasattr(os, "killpg"), reason="POSIX process groups")
BODY = "---\nname: foo\ndescription: Use when formatting dates as ISO.\n---\n# Dates\nUse strftime.\n"


def queued(root, run_id):
    intent_queue.append(run_id, {"action": "create", "name": "foo", "level": "project",
        "body": BODY, "reason": "owned regression", "evidence": "owned fixture"}, root)


def owner_path(root, run_id):
    return layer.state_dir(layer.PROJECT, root) / "run_owners" / f"{run_id}.json"


def env():
    result = dict(os.environ)
    result["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    return result


def dead_group():
    child = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)
    child.wait(timeout=5)
    return child.pid


def abandoned(root, run_id="dead"):
    queued(root, run_id)
    path = owner_path(root, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"version": 1, "status": "active", "process_groups": [dead_group()]}), encoding="utf-8")
    return path


def test_session_start_recovers_dead_owned_queue_and_surfaces_account(tmp_path):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    path = abandoned(roots["project"])
    result = on_session_start.on_session_start(roots=roots)
    assert skill_store.exists("project", "foo", roots["project"])
    assert "landed 1" in result["context"]
    assert not intent_queue._path("dead", roots["project"]).exists()
    assert json.loads(path.read_text())["status"] == "complete"


def test_live_child_prevents_adoption_after_supervisor_exits(tmp_path):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    code = """import json,subprocess,sys,time
from pathlib import Path
from autoharness.hook import recovery
recovery.track('live', Path(sys.argv[1]))
child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])
print(json.dumps({'child':child.pid}),flush=True)
time.sleep(60)
"""
    supervisor = subprocess.Popen([sys.executable, "-c", code, str(roots["project"])],
        env=env(), start_new_session=True, stdout=subprocess.PIPE, text=True)
    try:
        child = json.loads(supervisor.stdout.readline())["child"]
        queued(roots["project"], "live")
        supervisor.terminate()
        supervisor.wait(timeout=5)
        os.kill(child, 0)
        on_session_start.on_session_start(roots=roots)
        assert intent_queue._path("live", roots["project"]).exists()
        assert owner_path(roots["project"], "live").exists()
        assert not skill_store.exists("project", "foo", roots["project"])
    finally:
        try:
            os.killpg(supervisor.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        supervisor.wait(timeout=5)
        supervisor.stdout.close()


def test_retryable_filesystem_failure_retains_queue_and_owner(tmp_path, monkeypatch):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    path = abandoned(roots["project"])
    actual = promoter.promote
    def denied(*args, **kwargs):
        raise PermissionError("owned transient denial")
    monkeypatch.setattr(promoter, "promote", denied)
    on_session_start.on_session_start(roots=roots)
    assert path.exists()
    assert intent_queue._path("dead", roots["project"]).exists()
    monkeypatch.setattr(promoter, "promote", actual)
    on_session_start.on_session_start(roots=roots)
    assert skill_store.exists("project", "foo", roots["project"])
    assert json.loads(path.read_text())["status"] == "complete"


def test_writer_in_new_session_prevents_adoption_after_supervisor_exits(tmp_path):
    from autoharness.hook import recovery
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    proposal = {"action": "create", "name": "foo", "level": "project", "body": BODY,
                "reason": "owned regression", "evidence": "owned fixture"}
    writer_code = f"""from pathlib import Path
import os,sys,time
from autoharness.lib import intent_queue
intent_queue.append('escaped', {proposal!r}, Path(sys.argv[1]))
print(os.getpid(), flush=True)
time.sleep(60)
"""
    supervisor_code = f"""from pathlib import Path
import subprocess,sys
from autoharness.hook import recovery
recovery.track('escaped', Path(sys.argv[1]))
child=subprocess.Popen([sys.executable,'-c',{writer_code!r},sys.argv[1]],
    start_new_session=True,stdout=subprocess.PIPE,text=True)
print(child.stdout.readline().strip(),flush=True)
"""
    supervisor = subprocess.Popen([sys.executable, "-c", supervisor_code, str(roots["project"])],
        env=env(), start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    writer = None
    try:
        writer = int(supervisor.stdout.readline())
        supervisor.wait(timeout=5)
        assert supervisor.returncode == 0
        os.kill(writer, 0)
        owner = json.loads(owner_path(roots["project"], "escaped").read_text())
        assert set(owner["process_groups"]) == {supervisor.pid, writer}
        assert recovery.recover(roots=roots) == []
        assert not skill_store.exists("project", "foo", roots["project"])
        assert intent_queue._path("escaped", roots["project"]).exists()
    finally:
        if writer is not None:
            try:
                os.killpg(writer, signal.SIGTERM)
            except ProcessLookupError:
                pass
        if supervisor.poll() is None:
            supervisor.terminate()
        supervisor.wait(timeout=5)
        supervisor.stdout.close()
        supervisor.stderr.close()


def test_completed_owner_rejects_late_append_without_recreating_queue(tmp_path):
    from autoharness.hook import recovery
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    abandoned(roots["project"])
    assert recovery.recover(roots=roots) == ["dead"]
    account = layer.state_dir("project", roots["project"]) / "runs" / "dead.json"
    before = account.read_bytes()
    with pytest.raises(BrokenPipeError):
        queued(roots["project"], "dead")
    assert not intent_queue._path("dead", roots["project"]).exists()
    assert account.read_bytes() == before


def test_complete_preserves_owner_when_writer_committed_after_drain(tmp_path):
    from autoharness.hook import recovery
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    path = abandoned(roots["project"])
    promoter.drain("dead", roots=roots)
    queued(roots["project"], "dead")
    recovery.complete(path)
    assert json.loads(path.read_text())["status"] == "active"
    assert intent_queue._path("dead", roots["project"]).exists()


def test_completed_account_survives_unconsumed_owner(tmp_path):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    path = abandoned(roots["project"])
    promoter.drain("dead", roots=roots)
    account = layer.state_dir("project", roots["project"]) / "runs" / "dead.json"
    before = account.read_bytes()
    on_session_start.on_session_start(roots=roots)
    assert account.read_bytes() == before
    assert json.loads(path.read_text())["status"] == "complete"


def test_concurrent_recovery_accounts_owned_run_once(tmp_path, monkeypatch):
    from autoharness.hook import recovery
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    path = abandoned(roots["project"])
    actual = promoter.promote
    entered = threading.Event()
    release = threading.Event()
    def slow(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        return actual(*args, **kwargs)
    monkeypatch.setattr(promoter, "promote", slow)
    results = []
    first = threading.Thread(target=lambda: results.append(recovery.recover(roots=roots)))
    second = threading.Thread(target=lambda: results.append(recovery.recover(roots=roots)))
    first.start()
    assert entered.wait(5)
    second.start()
    release.set()
    first.join(5)
    second.join(5)
    assert not first.is_alive() and not second.is_alive()
    assert sorted(results) == [[], ["dead"]]
    assert json.loads(path.read_text())["status"] == "complete"
    account = layer.state_dir("project", roots["project"]) / "runs" / "dead.json"
    assert json.loads(account.read_text())["verdicts"][0]["ok"]


def test_untracked_interactive_invalid_and_inaccessible_owners_are_not_adopted(tmp_path, monkeypatch):
    from autoharness.hook import recovery
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    for run_id, group in [("untracked", None), (config.INTERACTIVE_RUN_ID, dead_group()),
                          ("bad", True), ("inaccessible", 123456)]:
        queued(roots["project"], run_id)
        if group is not None:
            path = owner_path(roots["project"], run_id)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"version": 1, "status": "active", "process_groups": [group]}), encoding="utf-8")
    def inaccessible(group, sig):
        raise PermissionError("cannot inspect group")
    monkeypatch.setattr(recovery.os, "killpg", inaccessible)
    on_session_start.on_session_start(roots=roots)
    for run_id in ["untracked", config.INTERACTIVE_RUN_ID, "bad", "inaccessible"]:
        assert intent_queue._path(run_id, roots["project"]).exists()
    assert not skill_store.exists("project", "foo", roots["project"])


@pytest.mark.parametrize("curate", [False, True])
@pytest.mark.parametrize("crash", [False, True])
def test_real_detached_spawn_entry_tracks_and_consumes_or_recovers(tmp_path, curate, crash):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    proposal = {"action": "create", "name": "foo", "level": "project", "body": BODY,
                "reason": "owned regression", "evidence": "owned fixture"}
    argv = (["--curate", "owned", str(roots["project"]), str(roots["global"])] if curate else
            ["unused", "sid", "owned", str(roots["project"]), str(roots["global"])])
    code = f"""import sys
from pathlib import Path
from autoharness.hook import spawn,promoter
from autoharness.lib import intent_queue
root=Path(sys.argv[1]); global_root=Path(sys.argv[2])
def owned_run(*args, **kwargs):
    intent_queue.append('owned', {proposal!r}, root)
    if {crash!r}: raise OSError('owned crash before drain')
    return promoter.drain('owned',roots={{'project':root,'global':global_root}})
spawn.run=owned_run;spawn.run_curator=owned_run
spawn.capture.window=lambda *args: ('',0)
spawn.capture.digest=lambda *args: ''
spawn.main({argv!r})
"""
    process = subprocess.Popen([sys.executable, "-c", code, str(roots["project"]), str(roots["global"])],
        env=env(), start_new_session=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate(timeout=10)
    assert process.returncode == (1 if crash else 0), (stdout, stderr)
    owner = json.loads(owner_path(roots["project"], "owned").read_text())
    assert owner["status"] == ("active" if crash else "complete")
    on_session_start.on_session_start(roots=roots)
    assert skill_store.exists("project", "foo", roots["project"])
    assert json.loads(owner_path(roots["project"], "owned").read_text())["status"] == "complete"
