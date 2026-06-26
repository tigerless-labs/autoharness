"""MNG 分子埋点：`PreToolUse(Skill)` 那刻给被调符号 sidecar calls +1，纯观察不拦截。

mng.md：率分子 = 被调次数，存被调符号 sidecar、层无关（身份决定落哪层）。**零侵入红线——
只给自产符号计数**，绝不给原生 / 用户 skill 写 sidecar（碰它们即违反不碰宿主作品）。递归
guard 同 CAP：reflector 子会话不计。坏 / 未知 / 同名歧义符号 fail-safe 不崩宿主 hook。

ponytail: event 里符号身份的确切 key = Phase 0 spike（mng.md 待解）；现按几个候选字段容错抽。
"""
import os

from autoharness import config
from autoharness.lib import sidecar, skill_store


def _skill_name(event):
    nested = event.get("tool_input") if isinstance(event.get("tool_input"), dict) else {}
    for src in (event, nested):
        for key in ("skill_name", "skill", "name"):
            v = src.get(key)
            if isinstance(v, str) and v.strip():
                return v
    return None


def on_skill_call(event, *, roots=None):
    if os.environ.get(config.CHILD_SESSION_ENV):
        return {"counted": False, "reason": "recursion_guard"}
    roots = roots or {}
    name = _skill_name(event)
    if not name:
        return {"counted": False, "reason": "no_skill"}
    try:
        lyr = skill_store.find(name, roots)
    except ValueError:
        return {"counted": False, "reason": "bad_or_ambiguous"}
    if lyr is None:
        return {"counted": False, "reason": "not_managed"}
    root = roots.get(lyr)
    if not sidecar.is_agent_created(lyr, name, root):
        return {"counted": False, "reason": "not_agent_created"}
    calls = sidecar.bump_calls(lyr, name, root)
    return {"counted": True, "level": lyr, "name": name, "calls": calls}
