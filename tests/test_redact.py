from autoharness.lib import redact


def test_redacts_secrets_and_pii():
    raw = (
        "contact jane.doe@example.com or call 415-555-0132; "
        "AWS AKIAIOSFODNN7EXAMPLE; "
        "-----BEGIN RSA PRIVATE KEY----- blah; "
        "api_key=sk_live_abcd1234EFGH5678ijkl"
    )
    out = redact.redact(raw)
    for leak in [
        "jane.doe@example.com",
        "415-555-0132",
        "AKIAIOSFODNN7EXAMPLE",
        "BEGIN RSA PRIVATE KEY",
        "sk_live_abcd1234EFGH5678ijkl",
    ]:
        assert leak not in out, f"leaked: {leak}"
    assert "[REDACTED:" in out


def test_benign_text_unchanged():
    raw = "This skill formats dates and sorts a list of integers."
    assert redact.redact(raw) == raw


def test_idempotent():
    raw = "ping ops@corp.io now"
    once = redact.redact(raw)
    assert redact.redact(once) == once


def test_redacts_claude_hosted_addresses_and_identifiers():
    raw = ("open https://claude.ai/design/p/abc, call api.anthropic.com/v1/x, "
           "session 123e4567-e89b-12d3-a456-426614174000, bridge cse_0123456789abcdefghijKL")
    out = redact.redact(raw)
    for leak in ["claude.ai", "api.anthropic.com", "123e4567", "cse_0123456789abcdefghijKL"]:
        assert leak not in out, f"leaked: {leak}"
