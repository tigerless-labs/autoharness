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


def test_credit_card_luhn_gate_keeps_long_ids_as_evidence():
    raw = "snowflake 7350428044806844 ts 1759234567890 pk 4111111111111112"
    out = redact.redact(raw)
    for keep in ["7350428044806844", "1759234567890", "4111111111111112"]:
        assert keep in out, f"over-redacted: {keep}"
    assert "[REDACTED:pii:credit_card]" not in out


def test_credit_card_still_redacts_valid_numbers():
    raw = "visa 4111 1111 1111 1111, amex 378282246310005, and 4012888888881881"
    out = redact.redact(raw)
    for leak in ["4111 1111 1111 1111", "378282246310005", "4012888888881881"]:
        assert leak not in out, f"leaked: {leak}"
    assert out.count("[REDACTED:pii:credit_card]") == 3


def test_each_rule_reports_itself_and_placeholders_are_never_rematched():
    # a rule's placeholder must survive the rules ordered after it: `secret:<name>`
    # inside it is itself an api_key_assignment match once the name is long enough.
    cases = {
        "AKIAABCDEFGHIJKLMNOP": "[REDACTED:secret:aws_access_key_id]",
        "-----BEGIN RSA PRIVATE KEY-----": "[REDACTED:secret:private_key_block]",
        "ghp_abcdefghij0123456789": "[REDACTED:secret:github_token]",
        "xoxb-1234567890-abcdef": "[REDACTED:secret:slack_token]",
        "Authorization: Bearer glpat-AbCdEfGhIjKlMnOpQrStU": (
            "Authorization: [REDACTED:secret:bearer_token]"
        ),
        "api_key=sk_live_abcd1234EFGH5678ijkl": "[REDACTED:secret:api_key_assignment]",
    }
    for raw, expected in cases.items():
        out = redact.redact(raw)
        assert out == expected, f"{raw!r} -> {out!r}"
        assert "[REDACTED:[REDACTED:" not in out, f"nested placeholder for {raw!r}"


def test_overlapping_rules_keep_the_earlier_rule_in_the_file():
    # github_token is ordered before api_key_assignment; the wider assignment match
    # overlaps it, so the narrower, earlier rule owns the span.
    raw = "token = ghp_abcdefghij0123456789"
    assert redact.redact(raw) == "token = [REDACTED:secret:github_token]"


def test_unknown_validator_name_fails_loud_at_rule_load():
    import tempfile

    from autoharness.lib import redact as redact_mod

    bad = tempfile.NamedTemporaryFile("w", suffix=".toml", delete=False)
    bad.write(
        '[[pii]]\nname = "x"\npattern = \'a+\'\nvalidate = "nope"\n'
    )
    bad.close()
    try:
        redact_mod.redact("aaa", rules_path=bad.name)
    except ValueError as exc:
        assert "nope" in str(exc)
    else:
        raise AssertionError("unknown validator must raise, not silently pass through")
    finally:
        import os

        os.unlink(bad.name)


def test_secret_hits_honors_rule_validator(tmp_path):
    rules = tmp_path / "rules.toml"
    rules.write_text(
        '[[secret]]\nname = "checked_number"\npattern = \'[0-9]{11}\'\nvalidate = "luhn"\n'
    )

    assert redact.secret_hits("invalid 79927398714", rules) == []
    assert redact.secret_hits("valid 79927398713", rules) == ["checked_number"]


def test_private_key_block_redacts_body_and_end_line():
    raw = (
        "-----BEGIN OPENSSH PRIVATE KEY-----\n"
        "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ\n"
        "QyNTUxOQAAACDq1J2v9xR8fGqJ6p3W\n"
        "-----END OPENSSH PRIVATE KEY-----"
    )
    out = redact.redact(raw)
    for leak in [
        "BEGIN OPENSSH PRIVATE KEY",
        "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ",
        "QyNTUxOQAAACDq1J2v9xR8fGqJ6p3W",
        "END OPENSSH PRIVATE KEY",
    ]:
        assert leak not in out, f"leaked: {leak}"
    assert "[REDACTED:" in out
    assert redact.secret_hits(raw) == ["private_key_block"]


def test_truncated_private_key_block_redacts_to_end_of_text():
    # Capture windows clip records at CAPTURE_MAX_RECORD_BYTES, so a window can
    # hold a BEGIN without its END; the safe side is redacting to end of text.
    raw = (
        "prefix -----BEGIN RSA PRIVATE KEY-----\n"
        "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ\n"
        "trailing evidence text"
    )
    out = redact.redact(raw)
    assert "BEGIN RSA PRIVATE KEY" not in out
    assert "b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ" not in out
    assert "trailing evidence text" not in out
    assert out.startswith("prefix ")


def test_fine_grained_github_pat_is_redacted():
    pat = "github_pat_11ABCDEFG0abcdefghijkl_mnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123"
    raw = f"cloned with {pat} ok"
    assert redact.redact(raw) == "cloned with [REDACTED:secret:github_token] ok"
    assert redact.secret_hits(raw) == ["github_token"]
