import json

from autoharness.stage_skill import server


def test_queue_io_failure_is_tool_error(monkeypatch, tmp_path):
    def unavailable(*args):
        raise OSError("fixture unavailable")

    monkeypatch.setattr(server.intent_queue, "append", unavailable)
    reply = server.handle(
        {
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "stage_skill",
                "arguments": {
                    "action": "delete",
                    "name": "foo",
                    "reason": "r",
                    "evidence": "e",
                },
            },
        },
        run_id="test",
        root=tmp_path,
    )
    assert reply["result"]["isError"]
    result = json.loads(reply["result"]["content"][0]["text"])
    assert not result["ok"] and result["intent"] is None
    assert result["errors"] == [["queue", "unable to persist intent"]]
