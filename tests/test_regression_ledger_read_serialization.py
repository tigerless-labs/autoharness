from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pytest

from autoharness.lib import ledger, lock


def test_ledger_reader_waits_for_complete_append(tmp_path):
    path = ledger.path("project", "skill", tmp_path)
    path.parent.mkdir(parents=True)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with lock.file_lock(path.with_suffix(path.suffix + ".lock")):
            path.write_text('{"reason":')
            reader = pool.submit(ledger.read, "project", "skill", tmp_path)
            with pytest.raises(TimeoutError):
                reader.result(timeout=0.1)
            path.write_text('{"reason": "complete"}\n')
        assert reader.result(timeout=5) == [{"reason": "complete"}]


def test_ledger_appends_preserve_existing_provenance(tmp_path):
    ledger.append("project", "skill", {"reason": "one"}, tmp_path)
    first = ledger.path("project", "skill", tmp_path).read_bytes()
    ledger.append("project", "skill", {"reason": "two"}, tmp_path)
    assert ledger.path("project", "skill", tmp_path).read_bytes().startswith(first)
    assert ledger.read("project", "skill", tmp_path) == [
        {"reason": "one"},
        {"reason": "two"},
    ]


def test_ledger_append_waits_for_active_writer(tmp_path):
    ledger.append("project", "skill", {"reason": "one"}, tmp_path)
    path = ledger.path("project", "skill", tmp_path)
    before = path.read_bytes()
    with ThreadPoolExecutor(max_workers=1) as pool:
        with lock.file_lock(path.with_suffix(path.suffix + ".lock")):
            writer = pool.submit(
                ledger.append, "project", "skill", {"reason": "two"}, tmp_path
            )
            with pytest.raises(TimeoutError):
                writer.result(timeout=0.1)
            assert path.read_bytes() == before
        writer.result(timeout=5)
    assert ledger.read("project", "skill", tmp_path) == [
        {"reason": "one"},
        {"reason": "two"},
    ]


@pytest.mark.parametrize("archived", [False, True])
def test_missing_ledger_read_does_not_create_state(tmp_path, archived):
    root = tmp_path / "absent"
    assert ledger.read("project", "missing", root, archived=archived) == []
    assert not root.exists()
