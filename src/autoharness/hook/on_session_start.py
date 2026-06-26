"""MNG 惰性重算：SessionStart 那刻对累积账现算 → 归档失活符号，跑在本会话召回前。

mng.md：非常驻宿主无后台 sweep，故淘汰骑 SessionStart——读 sidecar（calls 分子 + anchor）+
层请求计数器（分母）累积水位、过 lifecycle 判定、把待归档名单逐个移出 live 树（archived 靠
移目录出召回、可逆）。判定只读累积量（不读本 session 看到什么）→ 任意 repo 的 SessionStart
同一结论。每会话一次、不节流。只管自产符号（原生 / 用户 skill 在池外，守零侵入）。

ponytail: 孤儿会话计数 GC（崩溃 session 残留）需会话存活信号才能安全扫（朴素扫会误删并发
会话的活计数），缺信号前不做——clear_session 原语已备（Phase 4），policy 留 cap.md/mng.md 待解。
"""
from autoharness import config
from autoharness.lib import counters, layer, lifecycle, sidecar, skill_store


def _members(lyr, root):
    skills = layer.skills_dir(lyr, root)
    if not skills.exists():
        return []
    members = []
    for path in skills.glob(f"*/{skill_store.SKILL_FILE}"):
        name = path.parent.name
        if not sidecar.is_agent_created(lyr, name, root):
            continue
        s = sidecar.read(lyr, name, root)
        members.append({"name": name, "calls": s.get("calls", 0), "anchor": s.get("anchor", 0)})
    return members


def on_session_start(event=None, *, roots=None):
    roots = roots or {}
    archived = {}
    for lyr in layer.LAYERS:
        root = roots.get(lyr)
        names = lifecycle.evaluate(
            _members(lyr, root), counters.request_count(lyr, root),
            maturity=config.MATURITY_THRESHOLD[lyr], capacity=config.CAPACITY[lyr],
        )
        for name in names:
            skill_store.archive(lyr, name, root)
        archived[lyr] = names
    return {"archived": archived}
