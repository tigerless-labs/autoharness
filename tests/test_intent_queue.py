import pytest

from autoharness.lib import intent_queue


def test_append_read_clear_roundtrip(tmp_path):
    intent_queue.append("run1", {"action": "create", "name": "a"}, tmp_path)
    intent_queue.append("run1", {"action": "patch", "name": "a"}, tmp_path)
    got = intent_queue.read("run1", tmp_path)
    assert [i["action"] for i in got] == ["create", "patch"]
    intent_queue.clear("run1", tmp_path)
    assert intent_queue.read("run1", tmp_path) == []  # cleared once processed


def test_read_does_not_delete_at_least_once(tmp_path):
    # read does not delete -> a crash between land and clear is reprocessed next time (at-least-once)
    intent_queue.append("run1", {"action": "create"}, tmp_path)
    assert intent_queue.read("run1", tmp_path)
    assert intent_queue.read("run1", tmp_path)  # still there on re-read


def test_orphans_lists_undrained_runs(tmp_path):
    intent_queue.append("run1", {"action": "create"}, tmp_path)
    intent_queue.append("run2", {"action": "create"}, tmp_path)
    assert set(intent_queue.orphans(tmp_path)) == {"run1", "run2"}
    intent_queue.clear("run1", tmp_path)
    assert intent_queue.orphans(tmp_path) == ["run2"]


def test_read_missing_run_empty(tmp_path):
    assert intent_queue.read("nope", tmp_path) == []
    assert intent_queue.orphans(tmp_path) == []


def test_run_id_traversal_rejected(tmp_path):
    with pytest.raises(ValueError):
        intent_queue.append("../evil", {"a": 1}, tmp_path)


class _SplitWriter:
    """Writes each record in two parts, so an unserialized appender is caught
    mid-line rather than relying on the OS to split a large write for us."""

    def __init__(self, handle, pause):
        self._handle = handle
        self._pause = pause

    def write(self, text):
        half = len(text) // 2
        self._handle.write(text[:half])
        self._handle.flush()
        self._pause()
        return self._handle.write(text[half:])

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._handle.__exit__(*exc)


def test_append_does_not_interleave_concurrent_writers(tmp_path, monkeypatch):
    # O_APPEND keeps a write whole only up to PIPE_BUF, and a staged skill body
    # runs past that. Two overlapping reflector runs can interleave mid-record,
    # and read() then raises on the unparseable line, so every later drain of
    # this run jams on the same byte.
    import json
    import threading
    import time
    from pathlib import Path

    real_open = Path.open

    def splitting_open(self, mode="r", *args, **kwargs):
        handle = real_open(self, mode, *args, **kwargs)
        if "a" in mode:
            return _SplitWriter(handle, lambda: time.sleep(0.05))
        return handle

    monkeypatch.setattr(Path, "open", splitting_open)

    def stage(name):
        intent_queue.append("run1", {"action": "create", "name": name, "body": "x" * 8192}, tmp_path)

    writers = [threading.Thread(target=stage, args=(f"skill{i}",)) for i in range(2)]
    for w in writers:
        w.start()
    for w in writers:
        w.join()

    monkeypatch.undo()

    raw = tmp_path / "autoharness" / "intents" / "run1.jsonl"
    lines = [ln for ln in raw.read_text().splitlines() if ln.strip()]
    for line in lines:
        json.loads(line)  # a torn record raises here
    assert sorted(i["name"] for i in intent_queue.read("run1", tmp_path)) == ["skill0", "skill1"]


def test_read_survives_a_torn_or_foreign_line(tmp_path):
    # a crash or full disk mid-append leaves half a line; it must not hide the rest of the queue
    intent_queue.append("run1", {"action": "create", "name": "a"}, tmp_path)
    p = tmp_path / "autoharness" / "intents" / "run1.jsonl"
    with p.open("ab") as f:
        f.write(b'{"action": "create", "name": "b", "body": "\xe2\x80\n')  # torn line, cut UTF-8
        f.write(b"[1, 2]\n")  # valid JSON, not an intent
    intent_queue.append("run1", {"action": "patch", "name": "a"}, tmp_path)
    got = intent_queue.read("run1", tmp_path)
    assert [i.get("action") for i in got] == ["create", None, None, "patch"]
    assert all(intent_queue.UNREADABLE in i for i in got[1:3])


def test_unicode_line_separators_inside_a_value_stay_one_intent(tmp_path):
    body = "alpha\u2028beta\u2029gamma\x85delta\x1cend"  # str.splitlines() breaks on each of these
    intent_queue.append("run1", {"action": "create", "name": "a", "body": body}, tmp_path)
    got = intent_queue.read("run1", tmp_path)
    assert len(got) == 1 and got[0]["body"] == body


def test_append_after_a_torn_tail_keeps_the_new_intent_whole(tmp_path):
    # a crash left half a line with no newline; the next staged intent must not glue onto it
    p = tmp_path / "autoharness" / "intents" / "run1.jsonl"
    p.parent.mkdir(parents=True)
    p.write_bytes(b'{"action": "create", "name": "x", "bo')
    intent_queue.append("run1", {"action": "create", "name": "b"}, tmp_path)
    got = intent_queue.read("run1", tmp_path)
    assert intent_queue.UNREADABLE in got[0] and got[1] == {"action": "create", "name": "b"}
