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
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read(lyr, name, root=None):
    p = path(lyr, name, root)
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
