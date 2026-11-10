import importlib
import json
import subprocess
import sys
import time

from autoharness import config
from autoharness.hook import promoter
from autoharness.lib import intent_queue, layer, notify

ROWS = [{"action": "create", "name": "ok1", "ok": True},
        {"action": "patch", "name": "ok2", "ok": True},
        {"action": "create", "name": "bad", "ok": False}]
GOOD = "---\nname: ok1\ndescription: use when ok\n---\nr"


def _capture(monkeypatch):
    calls = []

    def fake_run(argv, **kw):
        calls.append((argv, kw))
        return subprocess.CompletedProcess(argv, 0)

    monkeypatch.setattr(notify.subprocess, "run", fake_run)
    return calls


def _hook_script(tmp_path):
    """A NOTIFY_CMD that records what it was handed: stdin record, summary env, recursion guard."""
    out = tmp_path / "out.json"
    script = tmp_path / "hook.py"
    script.write_text("import json, os, sys\n"
                      f"open({str(out)!r}, 'w').write(json.dumps({{'record': json.load(sys.stdin), "
                      "'summary': os.environ['AUTOHARNESS_NOTIFY_SUMMARY'], "
                      f"'guard': os.environ.get({config.CHILD_SESSION_ENV!r})}}))\n")
    return f"{sys.executable} {script}", out


def test_knobs_default_off(monkeypatch):
    for var in ("AUTOHARNESS_NOTIFY", "AUTOHARNESS_NOTIFY_CMD", "AUTOHARNESS_NOTIFY_TIMEOUT_S"):
        monkeypatch.delenv(var, raising=False)
    importlib.reload(config)
    try:
        assert config.NOTIFY == "" and config.NOTIFY_CMD == "" and config.NOTIFY_TIMEOUT_S == 5
    finally:
        monkeypatch.undo()
        importlib.reload(config)


def test_knobs_normalize_mode_and_floor_timeout(monkeypatch):
    monkeypatch.setenv("AUTOHARNESS_NOTIFY", " Desktop ")
    monkeypatch.setenv("AUTOHARNESS_NOTIFY_TIMEOUT_S", "0")
    importlib.reload(config)
    try:
        assert config.NOTIFY == "desktop" and config.NOTIFY_TIMEOUT_S == 1
    finally:
        monkeypatch.undo()
        importlib.reload(config)


def test_summary_names_landed_and_rejected():
    assert notify.summary(ROWS) == "create ok1, patch ok2 · rejected: bad"
    assert notify.summary([]) == ""


def test_summary_strips_control_chars_and_caps_name():
    line = notify.summary([{"action": "create", "name": "a\nb\x1b" + "x" * 200, "ok": False}])
    assert "\n" not in line and "\x1b" not in line
    assert len(line) <= len("rejected: ") + 64


def test_summary_caps_the_listing():
    rows = [{"action": "create", "name": f"s{i}", "ok": True} for i in range(12)]
    assert notify.summary(rows) == "create s0, create s1, create s2, create s3, create s4 +7 more"


def test_summary_redacts_names():
    # a rejected intent's name is arbitrary model text — it leaves the machine only after redaction
    secret = "ghp_" + "a" * 36
    line = notify.summary([{"action": "create", "name": secret, "ok": False}])
    assert secret not in line and "REDACTED" in line


def test_nothing_sent_when_off(monkeypatch):
    calls = _capture(monkeypatch)
    notify.send({"run_id": "r", "verdicts": ROWS})
    assert calls == []


def test_desktop_passes_message_as_argv_on_macos(monkeypatch):
    monkeypatch.setattr(config, "NOTIFY", "desktop")
    monkeypatch.setattr(sys, "platform", "darwin")
    calls = _capture(monkeypatch)
    evil = [{"action": "create", "name": 'x" & do shell script "id', "ok": False}]
    notify.send({"run_id": "r", "verdicts": evil})
    (argv, _), = calls
    assert argv[0] == "osascript"
    # the model-supplied name reaches AppleScript only as an argv item, never inside a -e script
    scripts = [argv[i + 1] for i, a in enumerate(argv) if a == "-e"]
    assert all("do shell script" not in s for s in scripts)
    assert 'rejected: x" & do shell script "id' in argv


def test_desktop_uses_notify_send_on_linux_when_present(monkeypatch):
    monkeypatch.setattr(config, "NOTIFY", "desktop")
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(notify.shutil, "which", lambda b: "/usr/bin/notify-send")
    calls = _capture(monkeypatch)
    notify.send({"run_id": "r", "verdicts": ROWS})
    assert calls[0][0][:2] == ["notify-send", "autoharness"]


def test_desktop_silent_without_a_notifier(monkeypatch):
    monkeypatch.setattr(config, "NOTIFY", "desktop")
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(notify.shutil, "which", lambda b: None)
    calls = _capture(monkeypatch)
    notify.send({"run_id": "r", "verdicts": ROWS})
    assert calls == []


def test_command_gets_record_summary_and_recursion_guard(tmp_path, monkeypatch):
    cmd, out = _hook_script(tmp_path)
    monkeypatch.setattr(config, "NOTIFY_CMD", cmd)
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    notify.send({"run_id": "r1", "verdicts": ROWS})
    got = json.loads(out.read_text())
    assert got["record"]["run_id"] == "r1"
    assert [v["name"] for v in got["record"]["verdicts"]] == ["ok1", "ok2", "bad"]
    assert got["summary"] == "create ok1, patch ok2 · rejected: bad"
    # a notifier that launches `claude` must not be captured/reflected into a feedback loop
    assert got["guard"] == "1"


def test_missing_notifier_binary_never_raises(monkeypatch):
    monkeypatch.setattr(config, "NOTIFY", "desktop")
    monkeypatch.setattr(config, "NOTIFY_CMD", "/nonexistent/notifier")
    monkeypatch.setattr(sys, "platform", "darwin")

    def raising(*a, **kw):
        raise FileNotFoundError("no such binary")

    monkeypatch.setattr(notify.subprocess, "run", raising)
    notify.send({"run_id": "r", "verdicts": ROWS})


def test_bad_or_failing_command_never_raises(monkeypatch):
    for cmd in ("unbalanced 'quote", f"{sys.executable} -c 'raise SystemExit(3)'"):
        monkeypatch.setattr(config, "NOTIFY_CMD", cmd)
        notify.send({"run_id": "r", "verdicts": ROWS})


def test_hung_command_is_bounded_by_timeout(monkeypatch):
    monkeypatch.setattr(config, "NOTIFY_TIMEOUT_S", 1)
    monkeypatch.setattr(config, "NOTIFY_CMD", f"{sys.executable} -c 'import time; time.sleep(30)'")
    t0 = time.monotonic()
    notify.send({"run_id": "r", "verdicts": ROWS})
    assert time.monotonic() - t0 < 5


def test_drain_notifies_after_account_and_clear(tmp_path, monkeypatch):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    proot = roots["project"]
    intent_queue.append("n1", {"action": "create", "name": "ok1", "level": "project", "body": GOOD,
                               "reason": "r", "evidence": "e"}, proot)
    state = layer.state_dir("project", proot)
    seen = []
    monkeypatch.setattr(notify, "send", lambda rec: seen.append(
        (rec, (state / "runs" / "n1.json").exists(), (state / "last_run.json").exists(),
         intent_queue.read("n1", proot))))
    promoter.drain("n1", roots=roots)
    (rec, run_on_disk, last_on_disk, queue_left), = seen
    assert run_on_disk and last_on_disk and queue_left == []
    assert rec["run_id"] == "n1" and rec["verdicts"][0]["ok"]


def test_drain_completes_when_the_notifier_blows_up(tmp_path, monkeypatch):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    proot = roots["project"]
    intent_queue.append("n2", {"action": "create", "name": "ok1", "level": "project", "body": GOOD,
                               "reason": "r", "evidence": "e"}, proot)
    monkeypatch.setattr(config, "NOTIFY", "desktop")
    monkeypatch.setattr(config, "NOTIFY_CMD", "anything")
    monkeypatch.setattr(sys, "platform", "darwin")

    def boom(*a, **kw):
        raise RuntimeError("notifier exploded")

    monkeypatch.setattr(notify.subprocess, "run", boom)
    verdicts = promoter.drain("n2", roots=roots)
    assert verdicts[0]["ok"] and intent_queue.read("n2", proot) == []
