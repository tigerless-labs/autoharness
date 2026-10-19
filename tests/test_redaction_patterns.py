"""Verify tightened redaction patterns reduce false positives."""
import re
import tomllib
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent.parent / "src" / "autoharness" / "lib" / "redaction_rules.toml"

def _load_rules():
    data = tomllib.loads(RULES_PATH.read_text())
    return {r["name"]: re.compile(r["pattern"]) for cat in ("secret", "pii") for r in data.get(cat, [])}

def test_bearer_short_not_redacted():
    rules = _load_rules()
    text = "Authorization: Bearer mF_9.B5f-4.1JqM"
    assert not rules["bearer_token"].search(text)

def test_bearer_real_token_redacted():
    rules = _load_rules()
    text = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123def456"
    assert rules["bearer_token"].search(text)

def test_api_key_short_not_redacted():
    rules = _load_rules()
    text = "token = abc123def456"
    assert not rules["api_key_assignment"].search(text)

def test_api_key_real_value_redacted():
    rules = _load_rules()
    text = "api_key = abc123def456ghi789jkl012"
    assert rules["api_key_assignment"].search(text)
