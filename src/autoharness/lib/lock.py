"""Cross-process exclusive lock: an empty lock file next to the target, held for one critical section.

One primitive for every cross-process critical section (counters' read-modify-write, the promoter's
drain). A hook is a separate short-lived process, so "serial single writer" only holds inside one
process; two sessions on the same state dir (parallel worktrees remapped to one root, or a session
killed mid-pass leaving a detached promotion running) interleave at the file level.

The lock is advisory and lives on a dedicated path, never on the data file: the data file is replaced
atomically, so a lock held on the old inode would not exclude a writer that opened the new one. The
lock file is never deleted, so waiters always contend on the same inode; it is empty and carries no
state of its own.
"""
import errno
import sys
from contextlib import contextmanager
from pathlib import Path

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

    def _try_lock(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)

    def _unlock(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl

    def _lock(f):
        fcntl.flock(f, fcntl.LOCK_EX)

    def _try_lock(f):
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _unlock(f):
        fcntl.flock(f, fcntl.LOCK_UN)


@contextmanager
def file_lock(path):
    """Hold the lock named by `path` for the duration of the block, releasing it on any exit."""
    lock_path = Path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as lock_fd:
        _lock(lock_fd)
        try:
            yield
        finally:
            _unlock(lock_fd)


def held(path):
    """Liveness probe: True when some process currently holds the lock at `path`.

    Tries to take the lock without waiting instead of blocking on it: a lock that cannot be
    taken is held by a live process, one that can be taken is released immediately and reported
    free. Safe to call while holding other locks, because it never waits.
    """
    lock_path = Path(path)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as f:
        try:
            _try_lock(f)
        except OSError:
            return True
        _unlock(f)
        return False