"""Two passes on one project root must not interleave inside drain.

A hook is a separate short-lived process, so "serial single writer" only holds within one process.
Parallel worktrees remap to one root (lib/layer.py), and a killed session can leave a detached
promotion running, so two drains on the same state dir are the normal case rather than the exception.
Without the lock each pass reads the library without seeing the other's skill and each lands.
"""
import threading
import time

from autoharness.hook import promoter
from autoharness.lib import intent_queue

GOOD_BODY = "---\nname: foo\ndescription: Use when formatting a date as ISO.\n---\n# Foo\nUse strftime.\n"


def _roots(tmp_path):
    return {"global": tmp_path / "g", "project": tmp_path / "p"}


def _create(name="foo"):
    return {"action": "create", "name": name, "level": "project", "body": GOOD_BODY,
            "reason": "captured repeat", "evidence": "led slice"}


def _wait(predicate, timeout=5.0):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.01)

    return False


def test_concurrent_drains_do_not_interleave(tmp_path, monkeypatch):
    roots = _roots(tmp_path)
    proot = roots["project"]
    intent_queue.append("run-a", _create("alpha"), proot)
    intent_queue.append("run-b", _create("beta"), proot)

    inside = threading.Event()
    release = threading.Event()
    entered = []

    real_promote = promoter.promote

    def blocking_promote(intent, **kwargs):
        entered.append(intent["name"])
        inside.set()
        release.wait(timeout=5.0)
        return real_promote(intent, **kwargs)

    monkeypatch.setattr(promoter, "promote", blocking_promote)

    first = threading.Thread(target=promoter.drain, args=("run-a",), kwargs={"roots": roots})
    first.start()
    assert inside.wait(timeout=5.0), "first drain never reached promote"

    second = threading.Thread(target=promoter.drain, args=("run-b",), kwargs={"roots": roots})
    second.start()

    # The second drain must still be waiting on the lock, not reading the library in parallel.
    assert not _wait(lambda: len(entered) > 1, timeout=0.5), "drains interleaved inside the critical section"

    release.set()
    first.join(timeout=5.0)
    second.join(timeout=5.0)

    assert not first.is_alive() and not second.is_alive()
    assert sorted(entered) == ["alpha", "beta"]


def test_lock_does_not_span_project_roots(tmp_path, monkeypatch):
    # The lock is per root, not process-wide: a pass on one repo must not wait out another.
    roots = _roots(tmp_path)
    other = {"global": roots["global"], "project": roots["project"] / "other"}
    intent_queue.append("run-a", _create("alpha"), roots["project"])
    intent_queue.append("run-b", _create("beta"), other["project"])

    inside = threading.Event()
    release = threading.Event()
    entered = []

    real_promote = promoter.promote

    def blocking_promote(intent, **kwargs):
        entered.append(intent["name"])
        if intent["name"] == "alpha":
            inside.set()
            release.wait(timeout=5.0)
        return real_promote(intent, **kwargs)

    monkeypatch.setattr(promoter, "promote", blocking_promote)

    first = threading.Thread(target=promoter.drain, args=("run-a",), kwargs={"roots": roots})
    first.start()
    assert inside.wait(timeout=5.0), "first drain never reached promote"

    # Runs to completion while the first drain is still parked inside its critical section.
    other_thread = threading.Thread(target=promoter.drain, args=("run-b",), kwargs={"roots": other})
    other_thread.start()
    other_thread.join(timeout=5.0)

    assert not other_thread.is_alive(), "a drain on another root blocked behind the lock"

    release.set()
    first.join(timeout=5.0)

    assert sorted(entered) == ["alpha", "beta"]