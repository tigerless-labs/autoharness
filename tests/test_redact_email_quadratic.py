"""The email PII rule must stay linear on long runs without a usable `@`."""

import time

from autoharness.lib import redact


def test_email_rule_redacts_normal_addresses():
    out = redact.redact("contact jane.doe@example.com soon")
    assert "jane.doe@example.com" not in out
    assert "[REDACTED:pii:email]" in out


def test_email_rule_redacts_a_64_char_local_part_whole():
    local = "a" * 64
    out = redact.redact("mail " + local + "@example.com end")
    assert "@example.com" not in out
    assert "[REDACTED:pii:email]" in out


def test_email_rule_still_catches_an_over_long_local_part():
    # 65+ chars is not a valid local part, but the rule errs toward over-redaction:
    # the tail (up to the cap) plus the domain must still be caught, never leaked.
    out = redact.redact("mail " + "a" * 100 + "@example.com end")
    assert "@example.com" not in out
    assert "[REDACTED:pii:email]" in out


def test_email_rule_is_linear_on_a_long_local_part_run():
    # Regression for #276: with the unbounded `+`, redact() was quadratic on a
    # long run of local-part characters (4.5s at 80k on the reporting machine);
    # the {1,64} cap keeps every start position bounded, so 80k finishes fast.
    text = "x" * 80000
    start = time.perf_counter()
    out = redact.redact(text)
    elapsed = time.perf_counter() - start
    assert out == text, "benign run must be left unchanged"
    assert elapsed < 1.0, f"redact() took {elapsed:.2f}s on an 80k local-part run"
