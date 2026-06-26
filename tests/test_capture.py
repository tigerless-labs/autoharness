import json

from autoharness.hook import capture


def _write_transcript(p, exchanges):
    lines = []
    for user_text, assistant_text in exchanges:
        lines.append(json.dumps({"type": "user", "message": {"role": "user", "content": user_text}}))
        lines.append(json.dumps({"type": "assistant",
                                 "message": {"role": "assistant", "content": assistant_text}}))
    p.write_text("\n".join(lines) + "\n")


def _users(window_text):
    return [ln for ln in window_text.splitlines() if ln.startswith("user:")]


def test_window_takes_tail_n_exchanges(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [(f"q{i}", f"a{i}") for i in range(5)])
    w = capture.window(t, 2)
    assert "q3" in w and "q4" in w
    assert "q0" not in w and "q2" not in w


def test_window_size_equals_n_zero_overlap(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [(f"q{i}", f"a{i}") for i in range(10)])
    assert len(_users(capture.window(t, 3))) == 3


def test_window_redacts_egress(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [("my key is AKIAIOSFODNN7EXAMPLE", "mail me jane.doe@example.com")])
    w = capture.window(t, 1)
    assert "AKIAIOSFODNN7EXAMPLE" not in w
    assert "jane.doe@example.com" not in w
    assert "[REDACTED:" in w


def test_materialize_atomic_no_source_mutation(tmp_path):
    t = tmp_path / "transcript.jsonl"
    _write_transcript(t, [("secret AKIAIOSFODNN7EXAMPLE here", "ok")])
    before = t.read_bytes()
    dest = tmp_path / "state" / "window.md"
    out = capture.materialize(t, 1, dest)
    assert out == dest and dest.exists()
    assert t.read_bytes() == before  # 宿主 raw log 字节不变
    assert "AKIAIOSFODNN7EXAMPLE" not in dest.read_text()  # 物化窗已脱敏


def test_window_missing_transcript_empty(tmp_path):
    assert capture.window(tmp_path / "nope.jsonl", 5) == ""
