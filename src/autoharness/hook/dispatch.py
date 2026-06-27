"""Single dispatcher: the one entry point for all the plugin's hook events, routing by event name to the matching `on_*`.

architecture §execution lives only at the hook global layer: `hooks.json` points only at this file, every
pipeline execution step enters through this one door and is dispatched by `hook_event_name`; unknown /
missing event names are safely ignored (fail-safe — a new host event must not crash this plugin). E6
platform contract pins the details:
- `Stop` = once per turn (S6) → on Stop, +1 each to both layers' request counters (the MNG-rate
  denominator), then run CAP triggering; `SubagentStop` (reflector done, S4) is not routed, not counted.
- `PreToolUse`: `Skill` → MNG numerator instrumentation (identity in `tool_input`, S5); reflector
  `agent_type` (carried in the S3 payload) on `Write`/`Edit` → deny (plugin top-level backstop — a
  plugin agent does not honor its own hooks, S1).
- Triggering reflection starts in a detached background job (host-detach: do not block the host Stop);
  the spawn CLI entry connects to the promoter.

ponytail: detached launch is a fire-and-forget Popen; robustness of orphan / timeout isolation left for observation.
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
            counters.bump_request(layer.GLOBAL, roots.get(layer.GLOBAL))  # MNG denominator (per turn)
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
