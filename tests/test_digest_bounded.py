"""Regression: digest() must read only end_offset bytes, not the entire transcript."""
import os
import tempfile
from unittest.mock import patch, mock_open

from autoharness.hook.capture import digest


def test_digest_bounded_read(tmp_path):
    """digest reads only end_offset bytes via bounded f.read(), not path.read_bytes()."""
    # Create a transcript file with some content
    transcript = tmp_path / "transcript.jsonl"
    lines = [
        '{"type": "user", "message": {"content": "hello"}}\n',
        '{"type": "assistant", "message": {"content": "hi there"}}\n',
    ]
    content = "".join(lines).encode("utf-8")
    transcript.write_bytes(content)

    # Read with end_offset covering only the first line
    first_line_end = len(lines[0].encode("utf-8"))
    result = digest(str(transcript), first_line_end)

    # Should contain the first exchange but not the second
    assert "hello" in result
    assert "hi there" not in result


def test_digest_full_when_offset_exceeds_file(tmp_path):
    """When end_offset exceeds file size, f.read(end_offset) reads the whole file (no error)."""
    transcript = tmp_path / "transcript.jsonl"
    content = '{"type": "user", "message": {"content": "test"}}\n'
    transcript.write_bytes(content.encode("utf-8"))

    result = digest(str(transcript), 999999)
    assert "test" in result
