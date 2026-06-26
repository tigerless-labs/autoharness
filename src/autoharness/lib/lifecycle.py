"""MNG 判定：纯确定性，调用率 + 缓刑 + 容量竞争 → 产「待归档名单」。不碰盘。

mng.md：成存依据是**调用率**（被调次数 / 创建以来层请求数）非墙钟。缓刑护新（分母未过成熟阈值
= live 但不淘汰、不占上限）；毕业即审（满样本仍 calls==0 当场归档）；成熟存活池超上限按率升序
归档最低者。判定只读累积水位（sidecar calls + anchor、层请求计数），故任意 repo 的 SessionStart
同一结论。on_session_start 拿本名单逐个 skill_store.archive。

ponytail: 绝对底线规则（毕业审外的硬底线 Y）、滚动窗口率留后（mng.md 待解）。
"""


def _rate(calls, denom):
    return calls / denom if denom else 0.0


def evaluate(members, request_count, *, maturity, capacity):
    archive = set()
    survivors = []
    for m in members:
        denom = max(0, request_count - m.get("anchor", 0))
        if denom < maturity:
            continue  # 缓刑：live、不淘汰、不占上限
        calls = m.get("calls", 0)
        if calls == 0:
            archive.add(m["name"])  # 毕业即审：给够机会仍零调
            continue
        survivors.append((_rate(calls, denom), m["name"]))
    if len(survivors) > capacity:
        survivors.sort(key=lambda rn: rn)  # 率升序，率同按 name 稳定
        archive.update(name for _, name in survivors[: len(survivors) - capacity])
    return sorted(archive)
