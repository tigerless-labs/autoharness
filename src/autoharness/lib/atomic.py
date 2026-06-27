"""POSIX atomic-write primitive: same-dir temp + fsync + os.replace — live is never half-written.

validate-store's "the only way to persist = same-dir temp + os.replace" is implemented here alone;
skill_store / sidecar / counters all reuse it. A crash mid-write leaves only a same-dir .tmp orphan
(swept on skill_store startup); the target file is either the old content or the new content, never
a half-write.
"""
import os
import tempfile
from pathlib import Path


def write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_text(path, text):
    write_bytes(path, text.encode("utf-8"))
