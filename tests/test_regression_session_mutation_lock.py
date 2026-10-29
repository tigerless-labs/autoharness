import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import pytest

from autoharness.lib import counters


@pytest.mark.parametrize("mutation", [counters.reset_session, counters.clear_session])
def test_session_mutation_waits_for_active_increment(tmp_path, monkeypatch, mutation):
    counters.bump_session("sid", tmp_path)
    original = counters._read_int
    entered, release = threading.Event(), threading.Event()

    def paused_read(path):
        value = original(path)
        entered.set()
        assert release.wait(5)
        return value

    monkeypatch.setattr(counters, "_read_int", paused_read)
    with ThreadPoolExecutor(max_workers=2) as pool:
        bump = pool.submit(counters.bump_session, "sid", tmp_path)
        assert entered.wait(5)
        mutating = pool.submit(mutation, "sid", tmp_path)
        try:
            with pytest.raises(TimeoutError):
                mutating.result(timeout=0.1)
        finally:
            release.set()
        assert bump.result(timeout=5) == 2
        mutating.result(timeout=5)
    monkeypatch.setattr(counters, "_read_int", original)
    assert counters.session_count("sid", tmp_path) == 0
