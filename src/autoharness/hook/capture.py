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
