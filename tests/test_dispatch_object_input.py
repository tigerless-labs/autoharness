import io
import json

import pytest

from autoharness.hook import dispatch


@pytest.mark.parametrize("event", [None, [], ["Stop"], "Stop", 4, False])
def test_non_object_event_is_ignored_before_root_resolution(event, monkeypatch):
    def forbidden(*args):
        raise AssertionError("malformed input must not resolve host roots")

    monkeypatch.setattr(dispatch, "_roots", forbidden)
    assert dispatch.dispatch(event)["ignored"]


@pytest.mark.parametrize("event", [None, [], "Stop", 4])
def test_cli_returns_zero_for_valid_non_object_json(event, monkeypatch, capsys):
    monkeypatch.setattr(dispatch.sys, "stdin", io.StringIO(json.dumps(event)))
    assert dispatch.main() == 0
    assert capsys.readouterr().out == ""
