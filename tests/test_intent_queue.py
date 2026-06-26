import pytest

from autoharness.lib import intent_queue


def test_append_read_clear_roundtrip(tmp_path):
    intent_queue.append("run1", {"action": "create", "name": "a"}, tmp_path)
    intent_queue.append("run1", {"action": "patch", "name": "a"}, tmp_path)
    got = intent_queue.read("run1", tmp_path)
    assert [i["action"] for i in got] == ["create", "patch"]
    intent_queue.clear("run1", tmp_path)
    assert intent_queue.read("run1", tmp_path) == []  # 处理完清空


def test_read_does_not_delete_at_least_once(tmp_path):
    # read 不删 → 崩在 land 与 clear 之间下次仍补处理（at-least-once）
    intent_queue.append("run1", {"action": "create"}, tmp_path)
    assert intent_queue.read("run1", tmp_path)
    assert intent_queue.read("run1", tmp_path)  # 再读仍在


def test_orphans_lists_undrained_runs(tmp_path):
    intent_queue.append("run1", {"action": "create"}, tmp_path)
    intent_queue.append("run2", {"action": "create"}, tmp_path)
    assert set(intent_queue.orphans(tmp_path)) == {"run1", "run2"}
    intent_queue.clear("run1", tmp_path)
    assert intent_queue.orphans(tmp_path) == ["run2"]


def test_read_missing_run_empty(tmp_path):
    assert intent_queue.read("nope", tmp_path) == []
    assert intent_queue.orphans(tmp_path) == []


def test_run_id_traversal_rejected(tmp_path):
    with pytest.raises(ValueError):
        intent_queue.append("../evil", {"a": 1}, tmp_path)
