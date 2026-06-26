"""CAP 交接物：触发那刻从宿主 transcript 取脱敏 tail-N 窗，物化给 reflector 跨进程读。

cap.md：CAP 零内容拷贝——不触发不抄；触发时取最近 N exchange（N == reflect_every_n，与触发
节奏同数、零重叠），过 egress 红线（redact），原子物化到 handoff 路径。**绝不回写宿主 raw
log**（它不是我们的）。脱敏发生在「物化给下游那一刻」、非某份入口存储副本。

ponytail: exchange 切分 = 宿主格式假设（user 角色起新窗、字段容错抽 role/text）。真 Claude
Code .jsonl schema + compaction 下 tail-N 是否取到原始轮次 = Phase 0 live spike（cap.md 待解）；
解析按 fixture 测不变量，spike 定真格式后再校准。
"""
import json
from pathlib import Path

from autoharness.lib import atomic, redact


def _records(transcript_path):
    p = Path(transcript_path)
    if not p.exists():
        return []
    records = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _role(rec):
    return str(rec.get("role") or rec.get("type") or "")


def _text(rec):
    msg = rec.get("message") if isinstance(rec.get("message"), dict) else rec
    content = msg.get("content", msg.get("text", ""))
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                parts.append(str(block.get("text") or block.get("content") or ""))
            else:
                parts.append(str(block))
        return " ".join(p for p in parts if p)
    return str(content)


def _exchanges(records):
    exchanges, current = [], []
    for rec in records:
        if _role(rec).startswith("user") and current:
            exchanges.append(current)
            current = []
        current.append(rec)
    if current:
        exchanges.append(current)
    return exchanges


def window(transcript_path, n, *, rules_path=None):
    if n <= 0:
        return ""
    tail = _exchanges(_records(transcript_path))[-n:]
    lines = [f"{_role(rec)}: {_text(rec)}" for ex in tail for rec in ex]
    return redact.redact("\n".join(lines), rules_path)


def materialize(transcript_path, n, dest, *, rules_path=None):
    atomic.write_text(dest, window(transcript_path, n, rules_path=rules_path))
    return dest
