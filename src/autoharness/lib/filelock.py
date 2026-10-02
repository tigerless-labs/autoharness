"""Cross-process exclusive file lock, shared by the writers that read-modify-write
or append to a file a concurrent hook may touch at the same time.

Each hook event is its own short-lived process, so nothing in memory serializes
them; the lock is a sidecar file next to the data, never the data file itself,
so a lock held during a rewrite cannot be destroyed by that rewrite.
"""
import errno
import sys
from contextlib import contextmanager

if sys.platform == "win32":
    import msvcrt

    def _lock(f):
        # LK_LOCK gives up with EDEADLOCK after ~10s; retry to match flock's indefinite wait.
        while True:
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
                return
            except OSError as e:
                if e.errno != errno.EDEADLOCK:
                    raise

    def _unlock(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _lock(f):
        fcntl.flock(f, fcntl.LOCK_EX)

    def _unlock(f):
        fcntl.flock(f, fcntl.LOCK_UN)


@contextmanager
def exclusive(path):
    """Hold an exclusive lock keyed on `path` for the duration of the block."""
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as lock_fd:
        _lock(lock_fd)
        try:
            yield
        finally:
            _unlock(lock_fd)
