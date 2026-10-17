import pytest

from autoharness.stage_skill import server


@pytest.mark.parametrize(
    "params",
    [
        ["stage_skill"],
        42,
        "invalid",
        {"name": "stage_skill", "arguments": ["create"]},
        {"name": "stage_skill", "arguments": True},
    ],
)
def test_non_object_tool_params_rejected(params, tmp_path):
    reply = server.handle(
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": params},
        run_id="test",
        root=tmp_path,
    )
    assert reply["error"]["code"] == -32602
    assert not (tmp_path / "autoharness").exists()
