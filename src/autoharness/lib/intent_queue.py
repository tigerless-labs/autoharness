"""per-run intent 队列：writer=stage_skill(append) / reader=promoter(read+clear) 同源一份。

durable（崩溃补处理）：只 append 进 repo 层 state 区的 per-run 文件、不碰 skill 树。promoter
走 read → land（原子、幂等）→ clear：crash 在 land 与 clear 之间 → 文件还在、下次 orphans
扫到补处理（at-least-once + 原子 land = 实际 exactly-once）；极端没跑 → 零 land（fail-safe）。
"""
import json
import re

from autoharness.lib import layer

_SAFE_RUN = re.compile(r"^[A-Za-z0-9_-]+$")


def _path(run_id, root=None):
    if not isinstance(run_id, str) or not _SAFE_RUN.match(run_id):
        raise ValueError(f"unsafe run id: {run_id!r}")
    return layer.state_dir(layer.PROJECT, root) / "intents" / f"{run_id}.jsonl"


def append(run_id, intent, root=None):
    p = _path(run_id, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(intent, ensure_ascii=False) + "\n")


def read(run_id, root=None):
    p = _path(run_id, root)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]


def clear(run_id, root=None):
    p = _path(run_id, root)
    if p.exists():
        p.unlink()


def orphans(root=None):
    d = layer.state_dir(layer.PROJECT, root) / "intents"
    if not d.exists():
        return []
    return sorted(f.stem for f in d.glob("*.jsonl"))
