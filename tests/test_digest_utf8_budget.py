import json

from autoharness.hook import capture


def test_unicode_digest_is_bounded_in_bytes_and_keeps_recent_exchange(tmp_path):
    transcript = tmp_path / "raw.jsonl"
    records = [
        {"type": "user", "message": {"content": "界" * 10 + str(i)}} for i in range(6)
    ]
    transcript.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in records))
    result = capture.digest(transcript, transcript.stat().st_size, max_digest_bytes=85)
    assert len(result.encode("utf-8")) <= 85
    assert "界" * 10 + "5" in result
    assert "界" * 10 + "0" not in result


def test_digest_bounds_expanding_redactions(tmp_path):
    transcript = tmp_path / "raw.jsonl"
    transcript.write_text(
        json.dumps({"type": "user", "message": {"content": "X X tail"}})
    )
    rules = tmp_path / "rules.toml"
    rules.write_text('[[secret]]\nname = "long-redaction-placeholder"\npattern = "X"\n')
    result = capture.digest(
        transcript, transcript.stat().st_size, max_digest_bytes=30, rules_path=rules
    )
    assert len(result.encode("utf-8")) <= 30
    assert result.endswith("tail")
