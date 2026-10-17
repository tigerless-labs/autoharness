"""Recover queues owned by completed POSIX detached process groups.

A missing supervisor PID alone is insufficient: its reflector or MCP child can
still be staging intents. Queue append registers each writer's actual group,
including children that start a new session, under the same ownership lock as
adoption. Every registered group must disappear before recovery can proceed.
Untracked, interactive, inaccessible, or live groups stay untouched.
"""
import errno
import json
import logging
import os

from autoharness import config
from autoharness.hook import promoter
from autoharness.lib import intent_queue, layer, lock, run_owners

log = logging.getLogger(__name__)


def _owner_path(run_id, root):
    return run_owners.path(run_id, root)


def track(run_id, root):
    """Record only actual detached group leaders, before any child can stage."""
    if not hasattr(os, "killpg") or run_id == config.INTERACTIVE_RUN_ID:
        return None
    pid = os.getpid()
    if os.getpgrp() != pid:
        return None
    path = _owner_path(run_id, root)
    with lock.file_lock(path.with_suffix(".lock")):
        run_owners.write(path, {"version": 1, "status": "active", "process_groups": [pid]})
    return path


def complete(path):
    """Consume ownership only after the queue and account completed normally."""
    if path is not None:
        with lock.file_lock(path.with_suffix(".lock")):
            owner = json.loads(path.read_text(encoding="utf-8"))
            queue = path.parent.parent / "intents" / f"{path.stem}.jsonl"
            if not queue.exists():
                owner["status"] = "complete"
                run_owners.write(path, owner)


def _group_gone(group):
    if type(group) is not int or group <= 0:
        return False
    try:
        os.killpg(group, 0)
    except OSError as exc:
        return exc.errno == errno.ESRCH
    return False


def recover(*, roots):
    """SessionStart adopts tracked queues only after every writer group exits."""
    if not hasattr(os, "killpg"):
        return []
    root = roots.get(layer.PROJECT)
    directory = layer.state_dir(layer.PROJECT, root) / "run_owners"
    recovered = []
    for path in sorted(directory.glob("*.json")):
        run_id = path.stem
        try:
            if run_id == config.INTERACTIVE_RUN_ID or path != _owner_path(run_id, root):
                continue
            # Two SessionStart processes must not re-account the same queue.
            with lock.file_lock(path.with_suffix(".lock")):
                if not path.exists():
                    continue
                owner = json.loads(path.read_text(encoding="utf-8"))
                if (not isinstance(owner, dict) or type(owner.get("version")) is not int
                        or owner["version"] != 1):
                    continue
                groups = owner.get("process_groups")
                if (owner.get("status") != "active" or owner.get("unverified_writer")
                        or not isinstance(groups, list) or not groups
                        or not all(_group_gone(group) for group in groups)):
                    continue
                # A crash after clear but before consuming ownership must retain
                # its existing run account, rather than replacing it with empty.
                if intent_queue._path(run_id, root).exists():
                    promoter.drain(run_id, roots=roots)
                    recovered.append(run_id)
                owner["status"] = "complete"
                run_owners.write(path, owner)
        except (OSError, ValueError, TypeError):
            # A retryable drain failure leaves both ownership and queue intact;
            # damaged/unreadable ownership cannot establish a dead writer.
            log.exception("could not recover abandoned run %s", run_id)
    return recovered
