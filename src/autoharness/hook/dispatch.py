"""单 dispatcher：plugin 所有 hook 事件的唯一入口，按事件名路由到对应 `on_*`。

architecture §执行只在 hook 全局层：`hooks.json` 只指本文件，凡 pipeline 执行步从这扇门进、
按 `hook_event_name` 分发，未知 / 缺事件名安全忽略（fail-safe，宿主新增事件不致崩本 plugin）。
E6 平台契约定细节：
- `Stop`=每回合一次（S6）→ 收 Stop 时给两层请求计数器各 +1（MNG 率分母），再走 CAP 触发；
  `SubagentStop`（reflector 完成，S4）不路由、不计。
- `PreToolUse`：`Skill` → MNG 分子埋点（S5 身份在 `tool_input`）；reflector `agent_type`（S3 payload
  带）对 `Write`/`Edit` → deny（plugin 顶层 backstop——plugin agent 不认自带 hooks，S1）。
- 触发反思在 detached 后台作业里起（host-detach：不堵宿主 Stop），spawn CLI 入口接 promoter。

ponytail: detached launch 是 fire-and-forget Popen；孤儿 / 超时隔离的健壮性留观测。
"""
import json
import re
import subprocess
import sys

from autoharness import config
from autoharness.hook import on_session_end, on_session_start, on_skill_call, on_stop
from autoharness.lib import counters, layer

_SANITIZE = re.compile(r"[^A-Za-z0-9_-]")
_WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")


def _roots(roots):
    return roots or {lyr: layer.default_root(lyr) for lyr in layer.LAYERS}


def _run_id(result):
    sid = _SANITIZE.sub("", str(result.get("session_id") or "")) or "run"
    return f"{sid}-{result.get('count', 0)}"


def _is_reflector(event):
    at = str(event.get("agent_type") or "")
    return at == config.REFLECTOR_AGENT or at.endswith("reflector")


def _detached_launch(transcript_path, window_n, run_id, roots):
    subprocess.Popen(  # host-detach: fire-and-forget so the Stop hook returns immediately
        [sys.executable, "-m", "autoharness.hook.spawn",
         str(transcript_path), str(window_n), run_id,
         str(roots[layer.PROJECT]), str(roots[layer.GLOBAL])],
        start_new_session=True, stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def _reflect(event, result, roots, launch=None):
    transcript_path = event.get("transcript_path")
    if not transcript_path:
        return
    (launch or _detached_launch)(transcript_path, result.get("window_n", 0), _run_id(result), roots)


def dispatch(event, *, roots=None, reflect=None):
    name = event.get("hook_event_name")
    roots = _roots(roots)
    proot = roots.get(layer.PROJECT)
    fire = reflect or _reflect
    try:
        if name == "SessionStart":
            return {"handled": name, "result": on_session_start.on_session_start(event, roots=roots)}
        if name == "Stop":
            counters.bump_request(layer.GLOBAL, roots.get(layer.GLOBAL))  # MNG 分母（每回合）
            counters.bump_request(layer.PROJECT, proot)
            result = on_stop.on_stop(event, root=proot)
            if result.get("triggered"):
                fire(event, result, roots)
            return {"handled": name, "result": result}
        if name == "SessionEnd":
            result = on_session_end.on_session_end(event, root=proot)
            if result.get("triggered"):
                fire(event, result, roots)
            return {"handled": name, "result": result}
        if name == "PreToolUse":
            tool = event.get("tool_name")
            if tool == "Skill":
                return {"handled": name, "result": on_skill_call.on_skill_call(event, roots=roots)}
            if tool in _WRITE_TOOLS and _is_reflector(event):
                return {"deny": True, "reason": "reflector may only stage intents, not write files"}
            return {"ignored": True, "reason": "untracked PreToolUse"}
    except Exception as exc:  # fail-safe: a buggy handler must never crash the host hook
        return {"error": f"{type(exc).__name__}: {exc}"}
    return {"ignored": True, "reason": f"unrouted event: {name!r}"}


def _emit(verdict):
    if verdict.get("deny"):
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": verdict.get("reason", "denied"),
        }}))


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # malformed hook input → ignore, never crash the host
    _emit(dispatch(event))
    return 0


if __name__ == "__main__":
    sys.exit(main())
