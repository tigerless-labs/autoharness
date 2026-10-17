import pytest

from autoharness.hook import capture


@pytest.mark.parametrize("cap", [1, 4, 13, 20, 100])
def test_record_truncation_marker_counts_toward_byte_budget(cap):
    text = capture._clip("界" * 100, cap)
    assert len(text.encode("utf-8")) <= cap


def test_window_budget_includes_marker_and_redaction_expansion(tmp_path):
    transcript = tmp_path / "raw.jsonl"
    transcript.write_text("old-line\n" * 20 + "secret!\nTAIL\n", encoding="utf-8")
    rules = tmp_path / "rules.toml"
    rules.write_text('[[secret]]\nname = "expanded-placeholder"\npattern = "secret!"\n')
    before = transcript.read_bytes()
    text, offset = capture.window(transcript, max_window_bytes=35, rules_path=rules)
    assert len(text.encode("utf-8")) <= 35
    assert "secret!" not in text
    assert text.endswith("TAIL")
    assert offset == len(before)
    assert transcript.read_bytes() == before
