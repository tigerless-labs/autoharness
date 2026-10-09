"""LED: per-symbol append-only ledger (.ledger.jsonl). Append-only, never modified.

Entries carry their own data from the intent (reason/evidence), appended the moment promoter passes;
MNG records retirements; rejects are not recorded. This module only appends / reads, it does not
adjudicate content (redaction is in redact, required fields are in validate). Append-only guarantees
immutability: existing lines are never rewritten.

`evidence` is an opaque string. New entries carry a relative path into the symbol folder
(`references/evidence-<hash>.md`, the promoter-materialized redacted slice) instead of the inline
slice; entries written before folder-skills keep their inline string (append-only, never
rewritten). Readers must not assume either form.

ponytail: one JSON line per write, and under small entries a POSIX append is effectively atomic;
the strict-ordering lock for concurrent cross-process appends to the same symbol is deferred to mng
along with sidecar.
"""
import json

from autoharness.lib import layer

FILENAME = ".ledger.jsonl"


def path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / FILENAME


def append(lyr, name, entry, root=None):
    p = path(lyr, name, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    # a tail torn by a crash mid-append has no newline: start on a fresh line so this entry survives
    torn = p.exists() and p.stat().st_size > 0 and _last_byte(p) != b"\n"
    with p.open("a", encoding="utf-8") as f:
        f.write(("\n" if torn else "") + json.dumps(entry, ensure_ascii=False) + "\n")


def _last_byte(p):
    with p.open("rb") as f:
        f.seek(-1, 2)
        return f.read(1)


def read(lyr, name, root=None, *, archived=False):
    """archived=True reads the ledger that travelled with the symbol into .archive/ (whole-dir
    rename carries it), so retirement provenance stays readable after eviction."""
    p = (layer.archive_dir(lyr, root) / name / FILENAME) if archived else path(lyr, name, root)
    if not p.exists():
        return []
    out = []
    # "\n" only: json.dumps writes U+2028 and friends raw inside `reason`, and splitlines() would cut
    # an entry in two; a line torn by a crash mid-append is skipped, the rest of the provenance reads
    for line in p.read_text(encoding="utf-8", errors="replace").split("\n"):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
