"""A claimed summary belongs to its reader even if a new run completes."""
import threading
from pathlib import Path

from autoharness.hook import on_session_start, promoter


def _publish(root, run_id, count):
    promoter._account(run_id, [{"name": f"skill-{i}"} for i in range(count)],
                      [{"ok": True, "action": "create"} for _ in range(count)], root)


def test_summary_claim_survives_a_second_run_and_reader(tmp_path, monkeypatch):
    roots = {"project": tmp_path}
    _publish(tmp_path, "first-run", 1)
    reached = [threading.Event(), threading.Event()]
    release = [threading.Event(), threading.Event()]
    results, errors = {}, []
    original_read = Path.read_text

    def delayed_read(path, *args, **kwargs):
        if path.name.endswith(".consuming"):
            index = int(threading.current_thread().name[-1])
            reached[index].set()
            assert release[index].wait(5), "reader was not released"
        return original_read(path, *args, **kwargs)

    def consume(index):
        try:
            results[index] = on_session_start.last_run_summary(roots)
        except Exception as error:
            errors.append(error)

    monkeypatch.setattr(Path, "read_text", delayed_read)
    first = threading.Thread(target=consume, args=(0,), name="summary-reader-0")
    second = threading.Thread(target=consume, args=(1,), name="summary-reader-1")
    first.start()
    try:
        assert reached[0].wait(5), "first record was not claimed"
        _publish(tmp_path, "second-run", 2)
        second.start()
        assert reached[1].wait(5), "second record was not claimed"
        release[0].set()
        first.join(5)
        assert not first.is_alive()
    finally:
        release[0].set()
        release[1].set()
        first.join(5)
        if second.ident is not None:
            second.join(5)
    assert not second.is_alive()
    assert not errors
    assert results == {
        0: "autoharness last run (first-run): landed 1, rejected 0",
        1: "autoharness last run (second-run): landed 2, rejected 0",
    }
    assert on_session_start.last_run_summary(roots) is None
    assert not list((tmp_path / "autoharness").glob("*.consuming"))
