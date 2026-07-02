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
