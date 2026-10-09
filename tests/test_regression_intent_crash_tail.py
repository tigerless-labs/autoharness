import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pytest

from autoharness.lib import intent_queue, lock


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


def test_malformed_committed_record_is_not_silently_discarded(tmp_path):
    path = intent_queue._path("run", tmp_path)
    path.parent.mkdir(parents=True)
    path.write_text("not-json\n")
    with pytest.raises(json.JSONDecodeError):
        intent_queue.read("run", tmp_path)


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
