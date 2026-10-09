import pytest

from autoharness import config
from autoharness.hook import dispatch
from autoharness.lib import counters


@pytest.mark.parametrize("hook", ["Stop", "SessionEnd"])
def test_failed_detach_reaches_dispatch_and_stderr(tmp_path, monkeypatch, capsys, hook):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    monkeypatch.setattr(config, "CONSOLIDATE_EVERY_N", 0)
    monkeypatch.setattr(config, "REFLECT_EVERY_N", 1)

    def fail(*args, **kwargs):
        raise FileNotFoundError("missing-child-interpreter")

    monkeypatch.setattr(dispatch.subprocess, "Popen", fail)
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    counters.bump_session("safe-session", roots["project"])
    verdict = dispatch.dispatch(
        {
            "hook_event_name": hook,
            "session_id": "safe-session",
            "transcript_path": "unused.jsonl",
        },
        roots=roots,
    )
    assert "missing-child-interpreter" in verdict["error"]
    dispatch._emit(verdict)
    assert "missing-child-interpreter" in capsys.readouterr().err
