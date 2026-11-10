import io
import json

from autoharness.stage_skill import server


def test_nonobject_json_requests_return_error_and_continue_serving():
    output = io.StringIO()
    server.serve(io.StringIO('{broken\n42\n[]\nnull\n' + json.dumps({'jsonrpc': '2.0', 'id': 7, 'method': 'tools/list'}) + '\n'), output)
    replies = [json.loads(line) for line in output.getvalue().splitlines()]
    assert [r['error']['code'] for r in replies[:4]] == [-32700, -32600, -32600, -32600]
    assert all(r['id'] is None for r in replies[:4])
    assert replies[4]['id'] == 7 and replies[4]['result']['tools']


def _serve(*lines):
    output = io.StringIO()
    server.serve(io.StringIO("".join(line + "\n" for line in lines)), output)
    return [json.loads(line) for line in output.getvalue().splitlines()]


def test_non_object_params_are_invalid_params_and_the_server_keeps_serving():
    replies = _serve(
        json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': 5}),
        json.dumps({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'}),
    )
    assert replies[0]['id'] == 1 and replies[0]['error']['code'] == -32602
    assert replies[1]['id'] == 2 and replies[1]['result']['tools']


def test_unexpected_handler_error_is_internal_error_not_a_dead_server(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError('boom')

    monkeypatch.setattr(server, 'stage', boom)
    call = {'jsonrpc': '2.0', 'method': 'tools/call', 'params': {'name': server.TOOL_NAME, 'arguments': {}}}
    replies = _serve(
        json.dumps({**call, 'id': 1}),
        json.dumps(call),  # notification: no reply
        json.dumps({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'}),
    )
    assert [r['id'] for r in replies] == [1, 2]
    assert replies[0]['error']['code'] == -32603
    assert replies[1]['result']['tools']
