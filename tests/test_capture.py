import json

from autoharness.hook import capture


def _write_transcript(p, records):
    p.write_text("\n".join(json.dumps(r) for r in records) + "\n")


def _record(i, text=None):
    return {"type": "user", "message": {"role": "user", "content": text or f"q{i}"}}


def test_window_returns_raw_slice_and_new_offset(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(i) for i in range(3)])
    text, offset = capture.window(t)
    assert offset == t.stat().st_size
    for i in range(3):
        assert f"q{i}" in text
    assert json.loads(text.splitlines()[0])["type"] == "user"


def test_window_incremental_zero_overlap(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(0), _record(1)])
    first, offset = capture.window(t)
    with t.open("a") as f:
        f.write(json.dumps(_record(2)) + "\n")
    second, new_offset = capture.window(t, offset)
    assert "q2" in second
    assert "q0" not in second and "q1" not in second
    assert new_offset > offset


def test_window_bad_offset_resets_to_full(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(0)])
    for bad in (t.stat().st_size + 999, -5):
        text, offset = capture.window(t, bad)
        assert "q0" in text
        assert offset == t.stat().st_size


def test_window_clips_oversized_record(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(0, text="x" * 500), _record(1)])
    text, _ = capture.window(t, max_record_bytes=100)
    lines = text.splitlines()
    assert all(len(ln) < 200 for ln in lines)
    assert "truncated" in text
    assert "q1" in text


def test_window_total_cap_keeps_tail(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(i) for i in range(50)])
    text, offset = capture.window(t, max_window_bytes=300)
    assert len(text) < 1000
    assert "q49" in text and "q0" not in text
    assert "truncated" in text
    assert offset == t.stat().st_size


def test_window_redacts_egress(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(0, text="my key is AKIAIOSFODNN7EXAMPLE"),
                          _record(1, text="mail me jane.doe@example.com")])
    text, _ = capture.window(t)
    assert "AKIAIOSFODNN7EXAMPLE" not in text
    assert "jane.doe@example.com" not in text
    assert "[REDACTED:" in text


def test_window_never_mutates_source(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(0, text="secret AKIAIOSFODNN7EXAMPLE here")])
    before = t.read_bytes()
    capture.window(t)
    assert t.read_bytes() == before


def test_window_missing_transcript_empty(tmp_path):
    assert capture.window(tmp_path / "nope.jsonl") == ("", 0)


def _assistant(text=None, tool=None):
    content = []
    if text:
        content.append({"type": "text", "text": text})
    if tool:
        content.append({"type": "tool_use", "name": tool, "input": {"command": "secret-args"}})
    return {"type": "assistant", "message": {"role": "assistant", "content": content}}


def _tool_result(output):
    return {"type": "user", "message": {"role": "user", "content": [
        {"type": "tool_result", "content": output}]}}


def test_digest_keeps_text_and_tool_names_drops_outputs(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [
        _record(0, text="fix the login bug"),
        _assistant(text="Looking at auth.py", tool="Bash"),
        _tool_result("HUGE-TOOL-OUTPUT-" * 50),
        _assistant(text="Fixed by adding a null check."),
    ])
    end = t.stat().st_size
    d = capture.digest(t, end)
    assert "fix the login bug" in d
    assert "Looking at auth.py" in d
    assert "Bash" in d                      # tool name survives
    assert "HUGE-TOOL-OUTPUT" not in d      # tool result content dropped
    assert "secret-args" not in d           # tool input dropped too


def test_digest_only_covers_bytes_before_offset(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(0, text="early context")])
    end = t.stat().st_size
    with t.open("a") as f:
        f.write(json.dumps(_record(1, text="fresh window")) + "\n")
    d = capture.digest(t, end)
    assert "early context" in d
    assert "fresh window" not in d
    assert capture.digest(t, 0) == ""       # nothing before offset zero


def test_digest_keeps_only_last_n_exchanges(tmp_path):
    t = tmp_path / "transcript.jsonl"
    records = []
    for i in range(30):
        records.append(_record(i, text=f"question-{i}"))
        records.append(_assistant(text=f"answer-{i}"))
    _write_transcript(t, records)
    d = capture.digest(t, t.stat().st_size, max_exchanges=5)
    assert "question-29" in d and "answer-29" in d
    assert "question-24" not in d and "question-0" not in d


def test_digest_clips_records_and_total(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [_record(0, text="y" * 5000), _record(1, text="tail-mark")])
    d = capture.digest(t, t.stat().st_size, max_record_chars=100)
    assert "tail-mark" in d
    assert "y" * 200 not in d
    big = tmp_path / "big.jsonl"
    _write_transcript(big, [_record(i, text=f"m{i}-" + "z" * 150) for i in range(100)])
    d2 = capture.digest(big, big.stat().st_size, max_digest_bytes=500)
    assert len(d2) < 1200
    assert "m99-" in d2                      # tail kept when capped


def test_digest_redacts_and_survives_garbage(tmp_path):
    t = tmp_path / "transcript.jsonl"
    t.write_text("NOT-JSON{{{\n"
                 + json.dumps(_record(0, text="key AKIAIOSFODNN7EXAMPLE end")) + "\n"
                 + '{"type": "assistant", "message": null}\n')
    d = capture.digest(t, t.stat().st_size)
    assert "AKIAIOSFODNN7EXAMPLE" not in d
    assert "[REDACTED:" in d
    assert "NOT-JSON" not in d               # garbage lines skipped, no crash


def test_digest_missing_transcript_empty(tmp_path):
    assert capture.digest(tmp_path / "nope.jsonl", 100) == ""


class _CountingReader:
    """Wraps a binary file so a test can see how much it actually read."""

    def __init__(self, handle, log):
        self._handle = handle
        self._log = log

    def read(self, size=-1):
        chunk = self._handle.read(size)
        self._log.append(len(chunk))
        return chunk

    def seek(self, *args):
        return self._handle.seek(*args)

    def tell(self):
        return self._handle.tell()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._handle.__exit__(*exc)


def test_window_does_not_read_the_history_it_skips(tmp_path, monkeypatch):
    # A hook runs once per turn, and window() is told where the last one stopped.
    # Reading the whole transcript to slice that prefix away allocates every byte
    # of a long session's history to return the few hundred bytes added since.
    import builtins
    from pathlib import Path

    transcript = tmp_path / "transcript.jsonl"
    prefix = ("\n".join(json.dumps(_record(i, "old")) for i in range(5000)) + "\n").encode()
    tail = (json.dumps(_record(0, "fresh")) + "\n").encode()
    transcript.write_bytes(prefix + tail)

    read_sizes = []
    real_open, real_read_bytes = builtins.open, Path.read_bytes

    def counting_open(file, mode="r", *args, **kwargs):
        handle = real_open(file, mode, *args, **kwargs)
        return _CountingReader(handle, read_sizes) if "b" in mode else handle

    def counting_read_bytes(self):
        data = real_read_bytes(self)
        read_sizes.append(len(data))
        return data

    monkeypatch.setattr(capture, "open", counting_open, raising=False)
    monkeypatch.setattr(Path, "read_bytes", counting_read_bytes)

    text, new_offset = capture.window(transcript, offset=len(prefix))

    assert new_offset == len(prefix) + len(tail)
    assert "fresh" in text
    assert "old" not in text
    assert sum(read_sizes) < len(prefix), (
        f"read {sum(read_sizes)} bytes to return the last {len(tail)}; "
        f"the skipped history is {len(prefix)} bytes"
    )


def test_window_growth_after_size_snapshot_stays_after_watermark(tmp_path, monkeypatch):
    import builtins

    transcript = tmp_path / "transcript.jsonl"
    prefix = (json.dumps(_record(0, "old")) + "\n").encode()
    growth = (json.dumps(_record(1, "fresh")) + "\n").encode()
    transcript.write_bytes(prefix)

    real_open = builtins.open
    grew = False

    class GrowingReader:
        def __init__(self, handle):
            self._handle = handle

        def read(self, size=-1):
            return self._handle.read(size)

        def seek(self, offset, whence=0):
            nonlocal grew
            position = self._handle.seek(offset, whence)
            if whence == 2 and not grew:
                with real_open(transcript, "ab") as writer:
                    writer.write(growth)
                grew = True
            return position

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return self._handle.__exit__(*exc)

    def growing_open(file, mode="r", *args, **kwargs):
        return GrowingReader(real_open(file, mode, *args, **kwargs))

    monkeypatch.setattr(capture, "open", growing_open, raising=False)

    first, offset = capture.window(transcript, offset=len(prefix))
    second, new_offset = capture.window(transcript, offset=offset)

    assert first == ""
    assert offset == len(prefix)
    assert "fresh" in second
    assert new_offset == len(prefix) + len(growth)
