import pytest

from autoharness.lib import counters


def test_request_counter_per_layer_independent(tmp_path):
    g, p = tmp_path / "g", tmp_path / "p"
    assert counters.bump_request("global", g) == 1
    assert counters.bump_request("global", g) == 2
    assert counters.bump_request("project", p) == 1
    assert counters.request_count("global", g) == 2
    assert counters.request_count("project", p) == 1


def test_missing_counter_reads_zero(tmp_path):
    assert counters.request_count("project", tmp_path) == 0


def test_session_counter_bump_and_reset(tmp_path):
    sid = "abc-123"
    assert counters.bump_session(sid, tmp_path) == 1
    assert counters.bump_session(sid, tmp_path) == 2
    counters.reset_session(sid, tmp_path)
    assert counters.session_count(sid, tmp_path) == 0


def test_unknown_layer_rejected(tmp_path):
    with pytest.raises(ValueError):
        counters.bump_request("staging", tmp_path)


def test_session_id_traversal_rejected(tmp_path):
    with pytest.raises(ValueError):
        counters.bump_session("../evil", tmp_path)
