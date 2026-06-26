"""E5 — session-id -> transcript discovery, and compaction survival of tail-N.

Reproduces the host-observed facts CAP depends on, over real Claude Code
transcripts. Asserts the two invariants; prints what it saw.

Usage: python3 probe.py [PROJECT_TRANSCRIPT_DIR]
Defaults to this repo's project dir under ~/.claude/projects/.
"""
import json
import sys
from pathlib import Path

DEFAULT_DIR = Path.home() / ".claude/projects/-home-ryan-tigerless-ai-autoharness"


def records(path):
    for line in path.open():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def main(argv):
    proj = Path(argv[0]) if argv else DEFAULT_DIR
    files = sorted(proj.glob("*.jsonl"))
    assert files, f"no transcripts under {proj}"

    deterministic = 0
    for f in files:
        for o in records(f):
            sid = o.get("sessionId")
            if sid:
                assert sid == f.stem, f"{f.name}: sessionId {sid} != filename stem"
                deterministic += 1
                break
    print(f"[discovery] {len(files)} transcripts; filename stem == sessionId on {deterministic} "
          f"-> session-id maps to a deterministic path")

    compacted = []
    for f in files:
        recs = list(records(f))
        marks = [i for i, o in enumerate(recs) if o.get("isCompactSummary")]
        if not marks:
            continue
        tail = recs[marks[-1] + 1:]
        raw = [o for o in tail
               if o.get("type") in ("user", "assistant") and isinstance(o.get("message"), dict)]
        assert raw, f"{f.name}: no raw turns survive after compaction summary"
        compacted.append((f.name, len(marks), len(recs), len(raw)))
    for name, nmarks, total, raw in compacted:
        print(f"[compaction] {name}: {nmarks} summary record(s), {total} total records, "
              f"{raw} raw turns survive after the last summary")
    assert compacted, "no compacted transcript available to test tail survival"

    print("OK: session-id->path is deterministic; compaction appends a summary record but "
          "does not delete prior raw turns -> tail-N raw turns remain readable.")


if __name__ == "__main__":
    main(sys.argv[1:])
