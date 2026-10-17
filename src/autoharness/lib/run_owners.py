"""Writer ownership for tracked detached runs, serialized with queue adoption."""
import errno
import json
import os
import re
from contextlib import contextmanager

from autoharness.lib import atomic, layer, lock


def path(run_id, root):
    if not isinstance(run_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError(f"unsafe run id: {run_id!r}")
    return layer.state_dir(layer.PROJECT, root) / "run_owners" / f"{run_id}.json"


def write(target, owner):
    atomic.write_text(target, json.dumps(owner))


@contextmanager
def writer(run_id, root):
    """Register every writer's actual group before it can commit to a tracked queue.

    A completed tombstone prevents a late surviving writer from recreating a
    consumed queue. Untracked/legacy queues keep their existing manual policy.
    """
    target = path(run_id, root)
    if not target.exists():
        yield
        return
    with lock.file_lock(target.with_suffix(".lock")):
        owner = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(owner, dict) or owner.get("status") != "active":
            raise OSError(errno.EPIPE, "tracked run has completed or invalid ownership")
        groups = owner.get("process_groups")
        if (type(owner.get("version")) is not int or owner["version"] != 1
                or not isinstance(groups, list) or not groups
                or any(type(group) is not int or group <= 0 for group in groups)):
            raise OSError(errno.EINVAL, "tracked run has invalid writer groups")
        if hasattr(os, "getpgrp"):
            group = os.getpgrp()
            if group not in groups:
                groups.append(group)
                write(target, owner)
        else:
            owner["unverified_writer"] = True
            write(target, owner)
        yield
