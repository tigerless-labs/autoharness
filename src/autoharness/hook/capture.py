"""CAP handoff window: a raw byte slice of the host transcript since the last reflection — zero parsing.

cap.md + docs/plans/raw-capture.md: the transcript is the host's internal event log, not a chat log;
any role/text extraction here is a format assumption that live windows proved wrong (meta records as
empty roles, tool results as pseudo-user turns). So capture does not interpret the format at all —
the reflector (an LLM) reads raw JSONL fine. capture only moves bytes: slice from the session's byte
watermark to EOF, clip oversized records and the window total (tool dumps / base64 must not blow the
child context), pass the egress red line (redact), and hand the text plus the new watermark back to
the caller. **Never write back to the host raw log** (it is not ours). A missing / stale / negative
watermark (compaction rewrote the file) fails safe to a full re-read bounded by the window cap.
"""
import json
from pathlib import Path

from autoharness import config
from autoharness.lib import redact

TRUNCATION_MARK = "...[truncated]"


def _clip(line, cap):
    return line if len(line) <= cap else line[:cap] + TRUNCATION_MARK


def window(transcript_path, offset=0, *, max_record_bytes=None, max_window_bytes=None,
           rules_path=None):
    record_cap = max_record_bytes or config.CAPTURE_MAX_RECORD_BYTES
    window_cap = max_window_bytes or config.CAPTURE_MAX_WINDOW_BYTES
    path = Path(transcript_path)
    if not path.exists():
        return "", 0
    data = path.read_bytes()
    new_offset = len(data)
    if not 0 <= offset <= new_offset:
        offset = 0
    lines = [_clip(line, record_cap)
             for line in data[offset:].decode("utf-8", errors="replace").splitlines()]
    kept, total = [], 0
    for line in reversed(lines):
        total += len(line) + 1
        if total > window_cap:
            kept.append(TRUNCATION_MARK)
            break
        kept.append(line)
    return redact.redact("\n".join(reversed(kept)), rules_path), new_offset


def _digest_record(line, max_chars):
    record = json.loads(line)
    if record.get("type") not in ("user", "assistant"):
        return None
    role = record["type"]
    content = record["message"]["content"]
    if isinstance(content, str):
        parts = [content]
    else:
        parts = []
        for block in content:
            kind = block.get("type")
            if kind == "text" and block.get("text"):
                parts.append(block["text"])
            elif kind == "tool_use":
                parts.append(f"[tool: {block.get('name', '?')}]")
    if not parts:
        return None
    text = " ".join(p.strip() for p in parts if p.strip())
    if len(text) > max_chars:
        text = text[:max_chars] + TRUNCATION_MARK
    return role, text


def digest(transcript_path, end_offset, *, max_exchanges=None, max_record_chars=None,
           max_digest_bytes=None, rules_path=None):
    exchanges = max_exchanges or config.DIGEST_EXCHANGES
    record_chars = max_record_chars or config.DIGEST_MAX_RECORD_CHARS
    digest_cap = max_digest_bytes or config.DIGEST_MAX_BYTES
    path = Path(transcript_path)
    if not path.exists() or end_offset <= 0:
        return ""
    data = path.read_bytes()[:end_offset]
    kept, total, users_seen = [], 0, 0
    for line in reversed(data.decode("utf-8", errors="replace").splitlines()):
        try:
            entry = _digest_record(line, record_chars)
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError):
            continue
        if entry is None:
            continue
        role, text = entry
        rendered = f"{role}: {text}"
        total += len(rendered) + 1
        if total > digest_cap:
            kept.append(TRUNCATION_MARK)
            break
        kept.append(rendered)
        if role == "user":
            users_seen += 1
            if users_seen >= exchanges:
                break
    return redact.redact("\n".join(reversed(kept)), rules_path) if kept else ""
