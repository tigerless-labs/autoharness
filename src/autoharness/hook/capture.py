"""CAP handoff artifact: at trigger time, take a redacted tail-N window from the host transcript and materialize it for the reflector to read across processes.

cap.md: CAP copies zero content — no trigger, no copy; on trigger take the most recent N exchanges
(N == reflect_every_n, same count as the trigger cadence, zero overlap), pass the egress red line
(redact), and atomically materialize to the handoff path. **Never write back to the host raw log**
(it is not ours). Redaction happens at the moment of materializing to the downstream, not as a stored
copy at some entry point.

ponytail: exchange splitting = an assumption about the host format (a user role starts a new window,
role/text extracted with field-tolerant fallbacks). Whether tail-N captures the original turns under
the real Claude Code .jsonl schema + compaction = Phase 0 live spike (cap.md open); parsing is tested
on fixtures for invariants, recalibrated once the spike pins down the real format.
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
