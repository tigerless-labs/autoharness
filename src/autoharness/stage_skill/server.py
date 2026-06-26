"""stage_skill：reflector 的唯一写入面（emit-intent 提案工具）。

模型改 skill 只此一途——去通用 Write/Edit。本工具**只 append per-run intent 队列、不碰任何
skill 树**：成型 / 内容交叉引用 / 安全 / 落盘全在确定性 promoter（admission 模型，模型碰不到）。
tool 只前置「结构」，promoter 兜「成型 + 内容 + 安全 + 落盘」（防御纵深，确定性侧别全信工具面）。

- schema 强制：action enum；按 action 的 body|delta 必填与互斥；LED reason/evidence 必填；
  create 的 level enum（默认 project，update/patch/delete 的层由 promoter 按两层 find 解析）。
- 入参即时反馈：create/update 跑结构查（frontmatter + name/description，复用 validate.structure）
  + body 大小，让模型在 subagent 会话内当场改、不整轮重来。
- append 的 intent 形状与 promoter.promote 消费一致（patch 走顶层 old_string/new_string）。

ponytail: MCP stdio 进程外壳（serve）+ .mcp.json 注册缓 Phase 7——零依赖铁律禁引 mcp SDK、
wire 形态又依 Phase 0 MCP-scope spike 结论。本模块现交付确定性处理器：TOOL_SCHEMA（广告面）
+ stage（强制权威，条件式 body|delta 结构在此、非 JSON Schema 能净表达）。run_id/root 由
spawn（Phase 5）经环境注入，此处收作入参。
"""
import json
import os
import sys

from autoharness import config
from autoharness.lib import intent_queue, layer, validate

_ACTIONS = ("create", "update", "patch", "delete")
_BODY_ACTIONS = ("create", "update")
TOOL_NAME = "stage_skill"
_PROTOCOL_VERSION = "2024-11-05"

TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": list(_ACTIONS),
                   "description": "create=新建(带 level) / update=整篇覆盖 / patch=小改(delta) / delete=删"},
        "name": {"type": "string", "description": "skill 符号名"},
        "level": {"type": "string", "enum": list(layer.LAYERS),
                  "description": "仅 create；默认 project，global 高门槛"},
        "body": {"type": "string", "description": "create/update：完整 SKILL.md 全文"},
        "old_string": {"type": "string", "description": "patch：被替换原文（须唯一匹配 live）"},
        "new_string": {"type": "string", "description": "patch：替换新文"},
        "reason": {"type": "string", "description": "LED：为何改（必填）"},
        "evidence": {"type": "string", "description": "LED：触发证据切片（必填）"},
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
    if action in _BODY_ACTIONS:
        if not has_body:
            errors.append(("schema", f"{action} requires body"))
        if has_delta:
            errors.append(("schema", f"{action} takes body, not old_string/new_string"))
        if action == "create":
            level = params.get("level", layer.PROJECT)
            if level not in layer.LAYERS:
                errors.append(("schema", f"level must be one of {layer.LAYERS}, got {level!r}"))
    elif action == "patch":
        if has_body:
            errors.append(("schema", "patch takes old_string/new_string, not body"))
        if params.get("old_string") is None or params.get("new_string") is None:
            errors.append(("schema", "patch requires both old_string and new_string"))
    elif action == "delete":
        if has_body or has_delta:
            errors.append(("schema", "delete takes no body/delta"))
    return errors


def _content_errors(params):
    body = params.get("body")
    if body is None:
        return []
    errors = []
    if len(body.encode("utf-8")) > config.STAGE_MAX_BODY_BYTES:
        errors.append(("size", f"body exceeds {config.STAGE_MAX_BODY_BYTES} bytes"))
    errors += validate.structure(body)
    return errors


def _intent(params):
    action = params["action"]
    intent = {"action": action, "name": params["name"],
              "reason": params["reason"], "evidence": params["evidence"]}
    if action == "create":
        intent["level"] = params.get("level", layer.PROJECT)
    if action in _BODY_ACTIONS:
        intent["body"] = params["body"]
    elif action == "patch":
        intent["old_string"] = params["old_string"]
        intent["new_string"] = params["new_string"]
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
                            "serverInfo": {"name": TOOL_NAME, "version": "0.1.0"}})
    if method == "tools/list":
        return _ok(req_id, {"tools": [{"name": TOOL_NAME,
                                       "description": "reflector 唯一写入面：emit-intent，只 append "
                                                      "per-run intent 队列、不碰 skill 树",
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
