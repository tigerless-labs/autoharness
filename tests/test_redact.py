import pytest

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


_EACH_SECRET = [
    ("AKIAIOSFODNN7EXAMPLE", "[REDACTED:secret:aws_access_key_id]"),
    ("-----BEGIN RSA PRIVATE KEY-----", "[REDACTED:secret:private_key_block]"),
    ("token ghp_" + "a" * 36, "token [REDACTED:secret:github_token]"),
    ("xoxb-123456789012-abcdefghijkl", "[REDACTED:secret:slack_token]"),
    ("Authorization: Bearer glpat-AbCdEfGhIjKlMnOpQrStU", "Authorization: [REDACTED:secret:bearer_token]"),
    ("api_key=sk_live_abcd1234EFGH5678ijkl", "[REDACTED:secret:api_key_assignment]"),
]


@pytest.mark.parametrize("raw, expected", _EACH_SECRET)
def test_each_secret_keeps_its_own_placeholder(raw, expected):
    # a later rule must not rewrite an earlier placeholder: `secret:bearer_token` is not a key=value
    assert redact.redact(raw) == expected


def test_a_second_pass_leaves_placeholders_alone():
    # evidence is redacted twice: once in the captured window, again when it is materialized
    once = redact.redact("; ".join(raw for raw, _ in _EACH_SECRET) + "; mail jane.doe@example.com")
    assert redact.redact(once) == once


def test_a_made_up_placeholder_does_not_shield_a_secret():
    # only this rule set's own placeholders are protected; anything else is raw text
    out = redact.redact("[REDACTED:secret:AKIAIOSFODNN7EXAMPLE] and [REDACTED:secret:ghp_" + "c" * 36 + "]")
    assert "AKIAIOSFODNN7EXAMPLE" not in out and "ghp_" not in out


def test_secret_hits_ignores_this_rule_sets_own_placeholders():
    # a skill may quote the redacted window it learned from; that is not a secret
    once = redact.redact("; ".join(raw for raw, _ in _EACH_SECRET))
    assert redact.secret_hits(once) == []
    assert "aws_access_key_id" in redact.secret_hits("[REDACTED:secret:AKIAIOSFODNN7EXAMPLE]")
