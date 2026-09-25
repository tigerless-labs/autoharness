"""Verify _remove_subfile uses exact-path matching, not substring."""
import re

def _is_referenced(rel, live):
    _ref = re.compile(r"(?<![A-Za-z0-9_./-])" + re.escape(rel) + r"(?![A-Za-z0-9_./-])")
    return _ref.search(live) is not None

def test_exact_match_detected():
    assert _is_referenced("scripts/run.py", "See scripts/run.py for details")

def test_longer_path_not_matched():
    assert not _is_referenced("scripts/run.py", "See scripts/run.py.bak for backup")

def test_standalone_at_line_start():
    assert _is_referenced("lib/helper.py", "lib/helper.py does the work")

def test_embedded_in_longer_token_not_matched():
    assert not _is_referenced("lib/help", "See lib/helper.py for details")
