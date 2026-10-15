import time

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



_SECRETS = [
    "AKIAABCDEFGHIJKLMNOP",
    "-----BEGIN RSA PRIVATE KEY-----",
    "ghp_abcdefghij0123456789",
    "xoxb-1234567890-abcdef",
    "Authorization: Bearer glpat-AbCdEfGhIjKlMnOpQrStU",
    "api_key=sk_live_abcd1234EFGH5678ijkl",
]


def test_a_second_pass_leaves_placeholders_alone():
    # evidence is redacted twice: once in the captured window, again when promoter materializes it
    once = redact.redact("; ".join(_SECRETS) + "; mail jane.doe@example.com")
    assert redact.redact(once) == once


def test_a_made_up_placeholder_does_not_shield_a_secret():
    # only this rule set's own placeholders are held; anything else is raw text
    out = redact.redact("[REDACTED:secret:AKIAIOSFODNN7EXAMPLE] and [REDACTED:secret:ghp_" + "c" * 36 + "]")
    assert "AKIAIOSFODNN7EXAMPLE" not in out and "ghp_" not in out


def test_secret_hits_ignores_this_rule_sets_own_placeholders():
    # a skill may quote the redacted window it learned from; that is not a secret
    assert redact.secret_hits(redact.redact("; ".join(_SECRETS))) == []
    assert "aws_access_key_id" in redact.secret_hits("[REDACTED:secret:AKIAIOSFODNN7EXAMPLE]")


def test_a_placeholder_inside_a_key_block_does_not_shield_the_block():
    # a match reaching outside a placeholder is raw: the block around it is still redacted and reported
    raw = "\n".join(["-----BEGIN RSA PRIVATE KEY-----", "Comment: [REDACTED:pii:email]",
                     "MIIEowIBAAKCAQEAyF2t", "-----END RSA PRIVATE KEY-----"])
    assert "MIIEowIBAAKCAQEAyF2t" not in redact.redact(raw)
    assert redact.secret_hits(raw) == ["private_key_block"]

def test_overlapping_matches_merge_and_the_earlier_rule_names_them():
    # github_token is ordered before api_key_assignment; the wider assignment match
    # overlaps it, so the narrower, earlier rule names the merged span.
    raw = "token = ghp_abcdefghij0123456789"
    assert redact.redact(raw) == "[REDACTED:secret:github_token]"


def test_a_match_inside_a_key_block_does_not_leave_the_block_raw():
    # the aws rule comes first and takes the id; dropping the overlapping key block kept its body
    raw = "\n".join(["-----BEGIN RSA PRIVATE KEY-----", "Comment: AKIAABCDEFGHIJKLMNOP",
                     "MIIEowIBAAKCAQEAyF2t", "-----END RSA PRIVATE KEY-----"]) + "\nafter"
    out = redact.redact(raw)
    for leak in ["BEGIN RSA", "AKIAABCDEFGHIJKLMNOP", "MIIEowIBAAKCAQEAyF2t", "END RSA"]:
        assert leak not in out, f"leaked: {leak}"
    assert out == "[REDACTED:secret:aws_access_key_id]\nafter"


def test_dense_matches_do_not_make_redact_quadratic():
    # 28k matches in a 200 KB window (the capture cap): checking each against every span took ~8 s
    started = time.perf_counter()
    out = redact.redact("a@b.co " * 28_000)
    assert time.perf_counter() - started < 2
    assert "a@b.co" not in out


def test_a_card_right_after_a_phone_number_is_still_found():
    # the phone and the card read as one 20-digit run whose first 16 digits fail luhn; finditer resumed
    # after that rejected match and never tried the card on its own
    out = redact.redact("call 415-555-0132 4111 1111 1111 1111 now")
    assert out.startswith("call [REDACTED:pii:us_phone] [REDACTED:pii:credit_card]") and "4111" not in out


def test_a_window_that_passes_luhn_by_chance_does_not_hide_the_rest_of_a_card():
    # `6026 1064 4111 1111` passes luhn; resuming after it left the real card's last eight digits raw
    out = redact.redact("6346 7486 6026 1064 4111 1111 1111 1111")
    assert "1111" not in out and out.endswith("[REDACTED:pii:credit_card]")


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
