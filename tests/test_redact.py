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


_BODY = ["b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ", "QyNTUxOQAAACDq1J2v9xR8fGqJ6p3W", "AAECAw=="]  # short tail line
_BEGIN, _END = "-----BEGIN OPENSSH PRIVATE KEY-----", "-----END OPENSSH PRIVATE KEY-----"


def _no_key_left(out):
    for leak in [_BEGIN, *_BODY, _END]:
        assert leak not in out, f"leaked: {leak}"


def test_private_key_block_redacts_the_body_not_just_the_header():
    out = redact.redact("before\n" + "\n".join([_BEGIN, *_BODY, _END]) + "\nafter")
    _no_key_left(out)
    assert out.startswith("before\n") and out.endswith("\nafter")


def test_private_key_block_in_a_json_escaped_transcript_record():
    # capture windows are transcript JSONL: the key's newlines are escaped, the block is one line
    record = '{"output": "' + "\\n".join([_BEGIN, *_BODY, _END]) + '\\nexit 0"}'
    out = redact.redact(record)
    _no_key_left(out)
    assert "exit 0" in out


def test_private_key_block_clipped_before_its_end_line():
    # a record clipped mid-key has no END: redact the rest of that record, keep the next one
    clipped = '{"output": "' + "\\n".join([_BEGIN, *_BODY]) + '"}\n{"next": "record"}'
    out = redact.redact(clipped)
    _no_key_left(out)
    assert '{"next": "record"}' in out
    raw = "\n".join([_BEGIN, *_BODY]) + "\nthe prose after it stays"
    out = redact.redact(raw)
    _no_key_left(out)
    assert "the prose after it stays" in out


def test_clipped_key_with_indented_or_padded_body_lines():
    # pasted inside a YAML block scalar, or with trailing spaces, and clipped before END (digest)
    indented = "  key: |\n    " + "\n    ".join([_BEGIN, *_BODY]) + "\n  other: value"
    padded = "\n".join([_BEGIN] + [ln + " " for ln in _BODY]) + "\nthe prose after it stays"
    for raw, kept in [(indented, "other: value"), (padded, "the prose after it stays")]:
        out = redact.redact(raw)
        _no_key_left(out)
        assert kept in out


def test_pgp_private_key_block_is_redacted_whole_and_clipped():
    begin, end = "-----BEGIN PGP PRIVATE KEY BLOCK-----", "-----END PGP PRIVATE KEY BLOCK-----"
    body = ["Version: GnuPG v2", "", "lQdGBGYAAAABEADKxAbCdEfGh", "=abcd"]
    after = "\nthe prose after it stays"
    for raw in ["\n".join([begin, *body, end]) + after, "\n".join([begin, *body]) + after]:
        out = redact.redact(raw)
        for leak in [begin, "GnuPG", "lQdGBGYAAAABEADKxAbCdEfGh", "=abcd", end]:
            assert leak not in out, f"leaked: {leak}"
        assert out.endswith(after)
    assert redact.secret_hits(begin) == ["private_key_block"]


def test_private_key_blocks_redact_separately():
    two = "\n".join([_BEGIN, *_BODY, _END, "between the keys", _BEGIN, *_BODY, _END])
    assert "between the keys" in redact.redact(two)


def test_clipped_key_does_not_swallow_records_up_to_a_later_keys_end():
    # a clipped key must not reach across records to the END of a later, complete key
    clipped = '{"output": "' + "\\n".join([_BEGIN, *_BODY]) + '"}'
    full = '{"output": "' + "\\n".join([_BEGIN, *_BODY, _END]) + '"}'
    out = redact.redact("\n".join([clipped, '{"diag": "kept"}', full]))
    _no_key_left(out)
    assert '{"diag": "kept"}' in out


def test_key_clipped_by_the_digest_record_cap():
    # capture.digest() cuts a record's text and appends its truncation mark to the cut line
    for cut in ("...[truncated]", "   ...[truncated]"):  # the cap can land inside trailing padding
        digest = "user: " + "\n    ".join([_BEGIN, *_BODY[:2]]) + cut + "\nassistant: done"
        out = redact.redact(digest)
        _no_key_left(out)
        assert "assistant: done" in out


def test_clipped_legacy_encrypted_key_redacts_its_headers_and_body():
    raw = "\n".join(["-----BEGIN RSA PRIVATE KEY-----", "Proc-Type: 4,ENCRYPTED",
                     "DEK-Info: AES-128-CBC,0123456789ABCDEF0123456789ABCDEF", "", *_BODY,
                     "prose after it stays"])
    out = redact.redact(raw)
    for leak in ["Proc-Type", "DEK-Info", *_BODY]:
        assert leak not in out, f"leaked: {leak}"
    assert "prose after it stays" in out


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
