"""stage_skill: the reflector's sole write surface (emit-intent proposal tool).

The model's only path to change a skill — instead of the generic Write/Edit. This tool **only appends to
the per-run intent queue, never touches any skill tree**: shaping / content cross-reference / security /
landing all live in the deterministic promoter (admission model, untouchable by the model). The tool only
front-checks "structure"; the promoter covers "shaping + content + security + landing" (defense in depth —
the deterministic side does not fully trust the tool surface).

- Schema enforcement: action enum; per-action body|delta|path required-and-mutually-exclusive; LED
  reason/evidence required; create's level enum (default project; the layer for update/patch/
  remove_file/delete is resolved by the promoter via a two-layer find).
- Instant feedback on args: create/update run a structure check (frontmatter + name/description, reusing
  validate.structure) + body size, so the model can fix it on the spot within the subagent session
  instead of redoing a whole turn.
- The appended intent's shape matches what promoter.promote consumes (patch uses top-level
  old_string/new_string).

ponytail: the MCP stdio process shell (serve) + .mcp.json registration is deferred to Phase 7 — the zero-dependency rule forbids pulling in an mcp SDK, and the wire form depends on the Phase 0 MCP-scope spike's conclusion. This module currently delivers the deterministic handler: TOOL_SCHEMA (the advertised surface) + stage (the enforced authority; the conditional body|delta structure lives here, not cleanly expressible in JSON Schema). run_id/root are injected via env by spawn (Phase 5) and received here as args.
"""
import json
import os
import sys

from autoharness import config
from autoharness.lib import intent_queue, layer, validate

_ACTIONS = ("create", "update", "patch", "remove_file", "delete")
_BODY_ACTIONS = ("create", "update")
TOOL_NAME = "stage_skill"
_PROTOCOL_VERSION = "2024-11-05"

TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": list(_ACTIONS),
                   "description": "create=new (with level) / update=replace whole file / patch=small edit (delta) / "
                                  "remove_file=drop one subfile / delete=remove the whole skill"},
        "name": {"type": "string", "description": "skill symbol name"},
        "level": {"type": "string", "enum": list(layer.LAYERS),
                  "description": "create only; defaults to project, global has a high bar"},
        "body": {"type": "string", "description": "create/update: full SKILL.md text"},
        "old_string": {"type": "string", "description": "patch: text to replace (must match the live copy uniquely)"},
        "new_string": {"type": "string", "description": "patch: replacement text"},
        "reason": {"type": "string", "description": "LED: why the change (required)"},
        "evidence": {"type": "string", "description": "LED: triggering evidence slice (required)"},
        "files": {"type": "object", "additionalProperties": {"type": "string"},
                  "description": "create/update only: subfiles as relative path -> content, under "
                                 "scripts/|templates/|assets/|references/; each must be referenced "
                                 "by its relative path in the SKILL.md body"},
        "path": {"type": "string",
                 "description": "remove_file only: relative path of the subfile to remove; the live "
                                "SKILL.md must no longer reference it (patch the pointer out first)"},
    },
    "required": ["action", "name", "reason", "evidence"],
}


def _nonempty(params, key):
    v = params.get(key)
    return isinstance(v, str) and bool(v.strip())


def _schema_errors(params):
    action = params.get("action")
    if action not in _ACTIONS:
        return [("schema", f"action must be one of {_ACTIONS}, got {action!r}")]
    errors = []
    if not _nonempty(params, "name"):
        errors.append(("schema", "name required (non-empty)"))
    if not _nonempty(params, "reason") or not _nonempty(params, "evidence"):
        errors.append(("schema", "LED reason+evidence required"))

    has_body = params.get("body") is not None
    has_delta = params.get("old_string") is not None or params.get("new_string") is not None
    has_files = params.get("files") is not None
    if action != "remove_file" and params.get("path") is not None:
        errors.append(("schema", f"{action} takes no path (path is remove_file only)"))
    if action in _BODY_ACTIONS:
        if not has_body:
            errors.append(("schema", f"{action} requires body"))
        if has_delta:
            errors.append(("schema", f"{action} takes body, not old_string/new_string"))
        if has_files and not isinstance(params["files"], dict):
            errors.append(("schema", "files must be an object of relative path -> content"))
        if action == "create":
            level = params.get("level", layer.PROJECT)
            if level not in layer.LAYERS:
                errors.append(("schema", f"level must be one of {layer.LAYERS}, got {level!r}"))
    elif action == "patch":
        if has_body:
            errors.append(("schema", "patch takes old_string/new_string, not body"))
        if params.get("old_string") is None or params.get("new_string") is None:
            errors.append(("schema", "patch requires both old_string and new_string"))
        if has_files:
            errors.append(("schema", "patch takes no files (use update to change subfiles)"))
    elif action == "remove_file":
        if not _nonempty(params, "path"):
            errors.append(("schema", "remove_file requires path"))
        if has_body or has_delta or has_files:
            errors.append(("schema", "remove_file takes only path, no body/delta/files"))
    elif action == "delete":
        if has_body or has_delta:
            errors.append(("schema", "delete takes no body/delta"))
        if has_files:
            errors.append(("schema", "delete takes no files"))
    return errors


def _content_errors(params):
    if params["action"] == "remove_file":
        return validate.check_remove_path(params["path"])
    body = params.get("body")
    if body is None:
        return []
    errors = []
    if len(body.encode("utf-8")) > config.STAGE_MAX_BODY_BYTES:
        errors.append(("size", f"body exceeds {config.STAGE_MAX_BODY_BYTES} bytes"))
    files = params.get("files")
    errors += validate.check_files(files)
    errors += validate.structure(body, files)
    return errors


def _intent(params):
    action = params["action"]
    intent = {"action": action, "name": params["name"],
              "reason": params["reason"], "evidence": params["evidence"]}
    if action == "create":
        intent["level"] = params.get("level", layer.PROJECT)
    if action in _BODY_ACTIONS:
        intent["body"] = params["body"]
        if params.get("files"):
            intent["files"] = params["files"]
    elif action == "patch":
        intent["old_string"] = params["old_string"]
        intent["new_string"] = params["new_string"]
    elif action == "remove_file":
        intent["path"] = params["path"]
    return intent


def stage(params, *, run_id, root=None):
    errors = _schema_errors(params)
    if not errors:
        errors += _content_errors(params)
    if errors:
        return {"ok": False, "errors": errors, "intent": None}
    intent = _intent(params)
    try:
        intent_queue.append(run_id, intent, root)
    except ValueError as exc:
        return {"ok": False, "errors": [("queue", str(exc))], "intent": None}
    return {"ok": True, "errors": [], "intent": intent}


def _ok(req_id, result):
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _err(req_id, code, message):
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle(request, *, run_id, root=None):
    method = request.get("method")
    req_id = request.get("id")
    if method == "initialize":
        return _ok(req_id, {"protocolVersion": _PROTOCOL_VERSION,
                            "capabilities": {"tools": {}},
                            "serverInfo": {"name": TOOL_NAME, "version": "0.2.0"}})
    if method == "tools/list":
        return _ok(req_id, {"tools": [{"name": TOOL_NAME,
                                       "description": "the reflector's sole write surface: emit-intent, only appends "
                                                      "to the per-run intent queue, never touches the skill tree",
                                       "inputSchema": TOOL_SCHEMA}]})
    if method == "tools/call":
        params = request.get("params") or {}
        if params.get("name") != TOOL_NAME:
            return _err(req_id, -32602, f"unknown tool: {params.get('name')}")
        out = stage(params.get("arguments") or {}, run_id=run_id, root=root)
        return _ok(req_id, {"content": [{"type": "text",
                                         "text": json.dumps(out, ensure_ascii=False, default=list)}],
                            "isError": not out["ok"]})
    if req_id is None:
        return None
    return _err(req_id, -32601, f"method not found: {method}")


def serve(stdin=None, stdout=None):
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    run_id = os.environ.get(config.RUN_ID_ENV, "")
    root = os.environ.get(config.PROJECT_ROOT_ENV) or None
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        response = handle(json.loads(line), run_id=run_id, root=root)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()


if __name__ == "__main__":
    serve()
