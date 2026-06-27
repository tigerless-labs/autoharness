import json

from autoharness import config
from autoharness.lib import intent_queue, layer
from autoharness.stage_skill import server

GOOD_BODY = "---\nname: foo\ndescription: Formats dates as ISO.\n---\n# Foo\nUse strftime.\n"
RUN = "run1"


def _params(**kw):
    base = {"action": "create", "name": "foo", "body": GOOD_BODY,
            "reason": "captured repeat", "evidence": "led slice"}
    base.update(kw)
    return base


def _errs(v):
    return {e[0] for e in v["errors"]}


def _queue(tmp_path):
    return intent_queue.read(RUN, tmp_path)


def test_tool_schema_advertises_contract():
    assert server.TOOL_SCHEMA["properties"]["action"]["enum"] == list(server._ACTIONS)
    assert set(server.TOOL_SCHEMA["required"]) == {"action", "name", "reason", "evidence"}


def test_create_appends_and_no_tree_write(tmp_path):
    v = server.stage(_params(), run_id=RUN, root=tmp_path)
    assert v["ok"], v["errors"]
    got = _queue(tmp_path)
    assert got == [{"action": "create", "name": "foo", "level": "project",
                    "body": GOOD_BODY, "reason": "captured repeat", "evidence": "led slice"}]
    assert not layer.skills_dir("project", tmp_path).exists()  # tool cannot touch the skill tree


def test_default_level_project(tmp_path):
    v = server.stage(_params(), run_id=RUN, root=tmp_path)
    assert v["ok"] and _queue(tmp_path)[0]["level"] == "project"


def test_explicit_global_level(tmp_path):
    v = server.stage(_params(level="global"), run_id=RUN, root=tmp_path)
    assert v["ok"] and _queue(tmp_path)[0]["level"] == "global"


def test_unknown_action_rejected_zero_append(tmp_path):
    v = server.stage(_params(action="frobnicate"), run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)
    assert _queue(tmp_path) == []


def test_missing_led_rejected(tmp_path):
    for kw in ({"reason": ""}, {"evidence": "  "}):
        v = server.stage(_params(**kw), run_id=RUN, root=tmp_path)
        assert not v["ok"] and "schema" in _errs(v)
    assert _queue(tmp_path) == []


def test_missing_name_rejected(tmp_path):
    v = server.stage(_params(name=""), run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)


def test_create_requires_body(tmp_path):
    p = _params()
    del p["body"]
    v = server.stage(p, run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)
    assert _queue(tmp_path) == []


def test_create_rejects_delta(tmp_path):
    v = server.stage(_params(old_string="a", new_string="b"), run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)


def test_patch_appends_old_new_no_body(tmp_path):
    v = server.stage({"action": "patch", "name": "foo", "old_string": "x", "new_string": "y",
                      "reason": "r", "evidence": "e"}, run_id=RUN, root=tmp_path)
    assert v["ok"], v["errors"]
    got = _queue(tmp_path)[0]
    assert got["old_string"] == "x" and got["new_string"] == "y" and "body" not in got


def test_patch_requires_both_delta(tmp_path):
    v = server.stage({"action": "patch", "name": "foo", "old_string": "x",
                      "reason": "r", "evidence": "e"}, run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)
    assert _queue(tmp_path) == []


def test_patch_rejects_body(tmp_path):
    v = server.stage({"action": "patch", "name": "foo", "body": GOOD_BODY,
                      "old_string": "x", "new_string": "y", "reason": "r", "evidence": "e"},
                     run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)


def test_delete_appends_no_body(tmp_path):
    v = server.stage({"action": "delete", "name": "foo", "reason": "r", "evidence": "e"},
                     run_id=RUN, root=tmp_path)
    assert v["ok"], v["errors"]
    assert _queue(tmp_path)[0] == {"action": "delete", "name": "foo", "reason": "r", "evidence": "e"}


def test_delete_rejects_body(tmp_path):
    v = server.stage({"action": "delete", "name": "foo", "body": GOOD_BODY,
                      "reason": "r", "evidence": "e"}, run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)


def test_bad_level_rejected_zero_append(tmp_path):
    v = server.stage(_params(level="planetary"), run_id=RUN, root=tmp_path)
    assert not v["ok"] and "schema" in _errs(v)
    assert _queue(tmp_path) == []


def test_frontmatter_feedback_blocks_append(tmp_path):
    v = server.stage(_params(body="# no frontmatter\njust text\n"), run_id=RUN, root=tmp_path)
    assert not v["ok"] and "structure" in _errs(v)
    assert _queue(tmp_path) == []  # bad structure -> zero append


def test_oversize_body_rejected(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "STAGE_MAX_BODY_BYTES", 10)
    v = server.stage(_params(), run_id=RUN, root=tmp_path)
    assert not v["ok"] and "size" in _errs(v)
    assert _queue(tmp_path) == []


def test_unsafe_run_id_surfaced_not_crash(tmp_path):
    v = server.stage(_params(), run_id="../evil", root=tmp_path)
    assert not v["ok"] and "queue" in _errs(v)


def test_stage_never_writes_skill_tree_any_action(tmp_path):
    server.stage(_params(), run_id=RUN, root=tmp_path)
    server.stage({"action": "delete", "name": "foo", "reason": "r", "evidence": "e"},
                 run_id=RUN, root=tmp_path)
    assert not layer.skills_dir("project", tmp_path).exists()
    assert not layer.archive_dir("project", tmp_path).exists()


# --- MCP stdio shell (zero-dep, hand-rolled JSON-RPC) ---

def _req(method, req_id=1, params=None):
    r = {"jsonrpc": "2.0", "method": method}
    if req_id is not None:
        r["id"] = req_id
    if params is not None:
        r["params"] = params
    return r


def test_handle_initialize_advertises_server(tmp_path):
    out = server.handle(_req("initialize"), run_id=RUN, root=tmp_path)
    assert out["result"]["serverInfo"]["name"] == server.TOOL_NAME
    assert out["result"]["protocolVersion"]


def test_handle_tools_list_carries_schema(tmp_path):
    out = server.handle(_req("tools/list"), run_id=RUN, root=tmp_path)
    tool = out["result"]["tools"][0]
    assert tool["name"] == server.TOOL_NAME
    assert tool["inputSchema"] is server.TOOL_SCHEMA


def test_handle_tools_call_routes_to_stage_and_appends(tmp_path):
    out = server.handle(_req("tools/call", params={"name": server.TOOL_NAME,
                                                    "arguments": _params()}),
                        run_id=RUN, root=tmp_path)
    assert out["result"]["isError"] is False
    assert intent_queue.read(RUN, tmp_path)  # the call really appended one intent


def test_handle_tools_call_bad_schema_is_error_not_crash(tmp_path):
    out = server.handle(_req("tools/call", params={"name": server.TOOL_NAME,
                                                   "arguments": {"action": "frobnicate"}}),
                        run_id=RUN, root=tmp_path)
    assert out["result"]["isError"] is True


def test_handle_unknown_tool_rejected(tmp_path):
    out = server.handle(_req("tools/call", params={"name": "evil", "arguments": {}}),
                        run_id=RUN, root=tmp_path)
    assert "error" in out


def test_handle_notification_returns_none(tmp_path):
    assert server.handle(_req("notifications/initialized", req_id=None),
                         run_id=RUN, root=tmp_path) is None


def test_serve_loops_stdin_to_stdout(tmp_path):
    import io
    stdin = io.StringIO(json.dumps(_req("initialize")) + "\n\n")
    stdout = io.StringIO()
    server.serve(stdin=stdin, stdout=stdout)
    line = stdout.getvalue().strip()
    assert json.loads(line)["result"]["serverInfo"]["name"] == server.TOOL_NAME
