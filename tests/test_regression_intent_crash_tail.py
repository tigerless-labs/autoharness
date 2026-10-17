import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pytest

from autoharness.hook import promoter
from autoharness.lib import intent_queue, layer, lock, skill_store


@pytest.mark.parametrize("tail", [b'{"body":', b'{"body": "\xe4\xbd'])
def test_crash_tail_does_not_jam_committed_records_or_future_appends(tmp_path, tail):
    path = intent_queue._path("run", tmp_path)
    path.parent.mkdir(parents=True)
    committed = b'{"body": "old"}\n'
    path.write_bytes(committed + tail)
    assert intent_queue.read("run", tmp_path) == [{"body": "old"}]
    assert path.read_bytes() == committed + tail  # reading never mutates the queue
    intent_queue.append("run", {"body": "new"}, tmp_path)
    assert intent_queue.read("run", tmp_path) == [{"body": "old"}, {"body": "new"}]
    assert path.read_bytes().startswith(committed)


def test_valid_record_without_newline_is_separated_before_append(tmp_path):
    path = intent_queue._path("run", tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text('{"body": "old"}')
    intent_queue.append("run", {"body": "new"}, tmp_path)
    assert intent_queue.read("run", tmp_path) == [{"body": "old"}, {"body": "new"}]


def test_malformed_committed_record_is_accounted_without_wedging_drain(tmp_path):
    roots = {"global": tmp_path / "g", "project": tmp_path / "p"}
    path = intent_queue._path("run", roots["project"])
    path.parent.mkdir(parents=True)
    path.write_text("not-json\n")
    verdicts = promoter.drain("run", roots=roots)
    assert len(verdicts) == 1 and not verdicts[0]["ok"]
    account = layer.state_dir("project", roots["project"]) / "runs" / "run.json"
    assert json.loads(account.read_text())["verdicts"][0]["findings"] == ["queue"]
    assert promoter.drain("run", roots=roots) == []


def _create(name):
    return {"action": "create", "name": name, "level": "project",
            "body": f"---\nname: {name}\ndescription: Use when formatting a date as ISO.\n---\n# X\nUse strftime.\n",
            "reason": "captured repeat", "evidence": "owned test"}


def test_append_during_landing_survives_next_drain(tmp_path, monkeypatch):
    import threading

    roots = {"global": tmp_path / "g", "project": tmp_path / "p"}
    proot = roots["project"]
    intent_queue.append("run", _create("foo"), proot)
    landed = threading.Event()
    release = threading.Event()
    writing = threading.Event()
    real = promoter.promote

    def paused(intent, **kwargs):
        landed.set()
        assert release.wait(5)
        return real(intent, **kwargs)

    def append():
        writing.set()
        intent_queue.append("run", _create("bar"), proot)

    monkeypatch.setattr(promoter, "promote", paused)
    with ThreadPoolExecutor(max_workers=2) as pool:
        drained = pool.submit(promoter.drain, "run", roots=roots)
        assert landed.wait(5)
        writer = pool.submit(append)
        assert writing.wait(5)
        try:
            # On the old reader-only lock the append returns here; clear then
            # deletes it. Both schedules must retain it for the second drain.
            writer.result(timeout=0.1)
        except TimeoutError:
            pass
        release.set()
        drained.result(timeout=5)
        writer.result(timeout=5)
    monkeypatch.setattr(promoter, "promote", real)
    promoter.drain("run", roots=roots)
    assert skill_store.exists("project", "foo", proot)
    assert skill_store.exists("project", "bar", proot)


def test_unicode_line_separator_stays_with_one_intent(tmp_path):
    value = {"body": "first\u2028second\u2029third\u0085last"}
    intent_queue.append("unicode", value, tmp_path)
    assert intent_queue.read("unicode", tmp_path) == [value]


def test_malformed_intent_does_not_block_healthy_neighbor(tmp_path):
    roots = {"global": tmp_path / "g", "project": tmp_path / "p"}
    proot = roots["project"]
    intent_queue.append("setup", _create("foo"), proot)
    promoter.drain("setup", roots=roots)
    intent_queue.append("run", {"action": "patch", "name": "foo", "old_string": 42,
                               "new_string": "replacement", "reason": "test", "evidence": "test"}, proot)
    intent_queue.append("run", _create("healthy"), proot)
    verdicts = promoter.drain("run", roots=roots)
    assert [v["ok"] for v in verdicts] == [False, True]
    assert verdicts[0]["findings"][0][0] == "crash"
    assert skill_store.exists("project", "healthy", proot)


def test_live_partial_append_is_not_treated_as_a_crash(tmp_path):
    path = intent_queue._path("run", tmp_path)
    path.parent.mkdir(parents=True)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with lock.file_lock(path.with_suffix(path.suffix + ".lock")):
            path.write_text('{"body":')
            reader = pool.submit(intent_queue.read, "run", tmp_path)
            with pytest.raises(TimeoutError):
                reader.result(timeout=0.1)
            path.write_text('{"body": "complete"}\n')
        assert reader.result(timeout=5) == [{"body": "complete"}]


def test_missing_intent_read_does_not_create_state(tmp_path):
    root = tmp_path / "absent"
    assert intent_queue.read("missing", root) == []
    assert not root.exists()
