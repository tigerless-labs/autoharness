"""per-符号 sidecar：created_by / 分子计数(calls) / 创建锚(anchor) / verification。

单一实现、随符号目录走层（promote/archive 的 mv 把含分子的它原子带走）。运维元数据走
sidecar、不进 SKILL.md frontmatter（护召回、不污染用户作品）。created_by:agent 是 MNG 的
成员资格钥匙 + promoter「只动自产」校验的依据。

ponytail: bump_calls 是读-改-写、跨进程非原子；并发同改一符号的锁见 mng 待解（与 promoter
单写者锁合一），unit 路径串行。
"""
import json

from autoharness.lib import atomic, layer

FILENAME = ".sidecar.json"


def path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / FILENAME


def read(lyr, name, root=None):
    p = path(lyr, name, root)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def write(lyr, name, data, root=None):
    atomic.write_text(path(lyr, name, root), json.dumps(data, ensure_ascii=False, indent=2))


def create(lyr, name, anchor, root=None):
    data = {"created_by": "agent", "calls": 0, "anchor": int(anchor), "verification": None}
    write(lyr, name, data, root)
    return data


def bump_calls(lyr, name, root=None):
    data = read(lyr, name, root)
    data["calls"] = data.get("calls", 0) + 1
    write(lyr, name, data, root)
    return data["calls"]


def is_agent_created(lyr, name, root=None):
    return read(lyr, name, root).get("created_by") == "agent"
