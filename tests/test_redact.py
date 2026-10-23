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
    digest = "user: " + "\n".join([_BEGIN, *_BODY]) + "\nthe rest of this record goes too\nassistant: next record"
    out = redact.redact(digest)
    _no_key_left(out)
    assert "the rest of this record" not in out and out.endswith("\nassistant: next record")


def test_clipped_key_body_goes_whatever_its_lines_look_like():
    # indented (a YAML block scalar), padded, or with spaces inside the base64 (openssl reads that):
    # the body of a clipped key is the rest of its record, not lines that happen to look like base64
    chunks = [ln[i:i + 16] for ln in _BODY for i in range(0, len(ln), 16)]
    layouts = ["\n    ".join([_BEGIN, *_BODY]), "\n".join([_BEGIN] + [ln + " " for ln in _BODY]),
               "\n".join([_BEGIN] + [" ".join(ln[i:i + 16] for i in range(0, len(ln), 16)) for ln in _BODY])]
    for layout in layouts:
        out = redact.redact("user: " + layout + "\nassistant: next record")
        for leak in [_BEGIN, *chunks]:
            assert leak not in out, f"leaked: {leak}"
        assert out.endswith("\nassistant: next record")



@pytest.mark.parametrize("eol", ["\r\n", "\r\r\n", "\r"])
def test_clipped_key_body_goes_whatever_its_line_endings(eol):
    # openssl reads a PEM with `\r\r\n` endings; a fallback that stopped at the first `\r` kept the body
    out = redact.redact("user: " + eol.join([_BEGIN, *_BODY]) + "\nassistant: next record")
    _no_key_left(out)
    assert out.endswith("\nassistant: next record")

def test_pgp_private_key_block_is_redacted_whole_and_clipped():
    begin, end = "-----BEGIN PGP PRIVATE KEY BLOCK-----", "-----END PGP PRIVATE KEY BLOCK-----"
    body = ["Version: GnuPG v2", "", "lQdGBGYAAAABEADKxAbCdEfGh", "=abcd"]
    for raw, after in [("\n".join([begin, *body, end]), "\nthe prose after it stays"),
                       ("\n".join([begin, *body]), "\nassistant: next record")]:
        out = redact.redact(raw + after)
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
                     "assistant: next record"])
    out = redact.redact(raw)
    for leak in ["Proc-Type", "DEK-Info", *_BODY]:
        assert leak not in out, f"leaked: {leak}"
    assert out.endswith("\nassistant: next record")


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


def test_fine_grained_github_pat_is_redacted():
    pat = "github_pat_11ABCDEFG0abcdefghijkl_mnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123"
    raw = f"cloned with {pat} ok"
    assert redact.redact(raw) == "cloned with [REDACTED:secret:github_token] ok"
    assert redact.secret_hits(raw) == ["github_token"]


def test_quoted_key_assignments_are_redacted():
    # JSON / Python-dict / TOML-style assignments quote the key, and inside a JSONL transcript record
    # the quotes are backslash-escaped: the value must not survive any of those spellings.
    # (no vendor prefix on purpose: this test is about the assignment rule alone, and secret_hits below
    # would also list the vendor-key rule for an sk_live_ value)
    secret = "abcd1234EFGH5678ijkl"
    for raw in (
        f'{{"api_key": "{secret}"}}',
        f'{{"password":"{secret}"}}',
        f"{{'token': '{secret}'}}",
        f'"client_secret" = "{secret}"',
        '{"type":"user","content":"{\\"api_key\\": \\"' + secret + '\\"}"}',
    ):
        out = redact.redact(raw)
        assert secret not in out, f"leaked in {raw!r}: {out!r}"
        assert "[REDACTED:secret:api_key_assignment]" in out
        assert redact.secret_hits(raw) == ["api_key_assignment"]


def test_quoted_key_rule_keeps_short_values_and_prose():
    raw = '{"token": "short"} and the "password" field is required'
    assert redact.redact(raw) == raw
