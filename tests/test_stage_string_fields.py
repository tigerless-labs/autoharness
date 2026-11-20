import pytest

from autoharness.lib import intent_queue
from autoharness.stage_skill import server


@pytest.mark.parametrize(
    "extra",
    [
        {"action": "create", "body": 42},
        {"action": "update", "body": {}},
        {"action": "patch", "old_string": 42, "new_string": "x"},
        {"action": "patch", "old_string": "x", "new_string": []},
        {"action": "delete", "absorbed_into": {"name": "other"}},
    ],
)
def test_non_string_fields_rejected(extra, tmp_path):
    params = {"name": "foo", "reason": "repeat", "evidence": "fixture", **extra}
    result = server.stage(params, run_id="test", root=tmp_path)
    assert not result["ok"] and result["intent"] is None
    assert any(family == "schema" for family, _ in result["errors"])
    assert intent_queue.read("test", tmp_path) == []


def test_empty_patch_replacement_still_supported(tmp_path):
    assert server.stage(
        {
            "action": "patch",
            "name": "foo",
            "reason": "r",
            "evidence": "e",
            "old_string": "x",
            "new_string": "",
        },
        run_id="test",
        root=tmp_path,
    )["ok"]
