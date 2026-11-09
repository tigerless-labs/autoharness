import io
import json

from autoharness.stage_skill import server


def test_malformed_line_does_not_drop_next_request():
    output = io.StringIO()
    server.serve(
        io.StringIO(
            "{broken\n"
            + json.dumps({"jsonrpc": "2.0", "id": 7, "method": "tools/list"})
            + "\n"
        ),
        output,
    )
    replies = [json.loads(line) for line in output.getvalue().splitlines()]
    assert replies[0]["error"]["code"] == -32700
    assert replies[0]["id"] is None
    assert replies[1]["id"] == 7 and replies[1]["result"]["tools"]
