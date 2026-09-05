"""Regression tests for dispatch: _detached_launch error handling + _run_id collision avoidance."""
from unittest.mock import patch

from autoharness.hook import dispatch


def test_run_id_empty_session_gets_hash():
    """A session_id that sanitizes to empty should produce a unique hash, not bare 'run'."""
    result = {"session_id": "...", "count": 5}
    rid = dispatch._run_id(result)
    assert rid != "run-5"
    assert rid.endswith("-5")
    # Two different session_ids that both sanitize to empty should differ
    r1 = dispatch._run_id({"session_id": "...", "count": 0})
    r2 = dispatch._run_id({"session_id": "???", "count": 0})
    assert r1 != r2


def test_run_id_normal_session_unchanged():
    """A normal session_id should still produce the expected format."""
    result = {"session_id": "abc-123", "count": 3}
    assert dispatch._run_id(result) == "abc-123-3"


def test_curate_run_id_empty_session_gets_hash():
    """Same hash fallback for _curate_run_id."""
    r1 = dispatch._curate_run_id({"session_id": "..."}, 10)
    r2 = dispatch._curate_run_id({"session_id": "???"}, 10)
    assert r1 != r2
    assert r1.endswith("-c10")


def test_detached_launch_oserror_returns_error():
    """If Popen raises OSError, _detached_launch returns an error dict instead of propagating."""
    with patch("autoharness.hook.dispatch.subprocess.Popen", side_effect=OSError("no interpreter")):
        result = dispatch._detached_launch("/tmp/t", "sid", "run-0", {"project": "/p", "global": "/g"})
    assert result is not None
    assert "error" in result
    assert "no interpreter" in result["error"]


def test_detached_launch_success_returns_none():
    """Normal Popen succeeds; _detached_launch returns None."""
    with patch("autoharness.hook.dispatch.subprocess.Popen"):
        result = dispatch._detached_launch("/tmp/t", "sid", "run-0", {"project": "/p", "global": "/g"})
    assert result is None
