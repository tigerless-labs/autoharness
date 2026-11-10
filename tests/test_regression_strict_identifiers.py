import pytest

from autoharness.lib import counters, intent_queue, layer


@pytest.mark.parametrize("name", ["skill\n", "skill\r\n", "skill\t", ".."])
def test_symbol_names_require_full_match(tmp_path, name):
    with pytest.raises(ValueError):
        layer.symbol_dir("project", name, tmp_path)
    with pytest.raises(ValueError):
        layer.subfile_path("project", "safe", f"scripts/{name}", tmp_path)


@pytest.mark.parametrize("sid", ["session\n", "session\r\n", "session/child"])
def test_state_identifiers_require_full_match(tmp_path, sid):
    with pytest.raises(ValueError):
        counters.bump_session(sid, tmp_path)
    with pytest.raises(ValueError):
        counters.write_session_offset(sid, 1, tmp_path)
    with pytest.raises(ValueError):
        intent_queue.append(sid, {}, tmp_path)
    assert not list(tmp_path.rglob("*.jsonl"))
