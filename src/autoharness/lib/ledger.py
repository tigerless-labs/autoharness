"""LED：per-符号 append-only 账本（.ledger.jsonl）。只增不改。

条目随 intent 自带（reason/evidence），promoter pass 那刻 append；MNG 退役补记；reject 不入账。
记动作 + 理由 + 证据（脱敏切片 + 宿主 log 指针）+ watermark。本模块只管「追加 / 读」，不裁决
内容（脱敏在 redact、字段必填在 validate）。append-only 守不可篡改：永不重写既有行。

ponytail: 一行 JSON 一次 write，小条目下 POSIX append 实际原子；跨进程并发追加同符号的严格
顺序锁与 sidecar 一并留 mng 待解。
"""
import json

from autoharness.lib import layer

FILENAME = ".ledger.jsonl"


def path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / FILENAME


def append(lyr, name, entry, root=None):
    p = path(lyr, name, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read(lyr, name, root=None):
    p = path(lyr, name, root)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
