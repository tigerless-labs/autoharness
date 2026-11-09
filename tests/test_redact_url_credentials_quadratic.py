"""The url_credentials secret rule must stay linear on long runs without a match."""

import time

from autoharness.lib import redact


def test_url_credentials_rule_redacts_normal_urls():
    out = redact.redact("deploy postgres://app:P@ss!w0rd#2026/ab@db.internal:5432/prod done")
    assert "postgres://" not in out
    assert "[REDACTED:secret:url_credentials]" in out
    assert "db.internal:5432/prod" in out


def test_url_credentials_rule_still_catches_a_credential_at_the_cap():
    # 512 chars is the credential-run cap; a login:password that long must still
    # be redacted as a unit (a longer one stays raw on purpose, see #291).
    out = redact.redact("https://deploy:" + "p" * 512 + "@example.com/artifact")
    assert "example.com/artifact" in out
    assert "[REDACTED:secret:url_credentials]" in out


def test_url_credentials_rule_still_catches_a_32_char_scheme():
    scheme = "a" + "b" * 30 + "+v1"
    out = redact.redact(scheme + "://user:secret@host.example/x")
    assert "://user" not in out
    assert "[REDACTED:secret:url_credentials]" in out


def test_url_credentials_rule_is_linear_on_a_scheme_run():
    # Regression for #291: the unbounded scheme `[a-z0-9+.-]*` was backtracked at
    # every word boundary to the end of letter/digit/dot/dash stretches, which is
    # quadratic on a long run; the {0,31} cap keeps every attempt bounded.
    text = "a.b-" * 40000
    start = time.perf_counter()
    out = redact.redact(text)
    elapsed = time.perf_counter() - start
    assert out == text, "benign run must be left unchanged"
    assert elapsed < 1.0, f"redact() took {elapsed:.2f}s on a 200k scheme run"


def test_url_credentials_rule_is_linear_on_a_credential_run_without_at_sign():
    # Regression for #291: the unbounded `[^\s]+@` scanned to the end of the
    # non-space run at every scheme://user: start; the {1,512} cap bounds it.
    text = "x://u:" * 40000
    start = time.perf_counter()
    out = redact.redact(text)
    elapsed = time.perf_counter() - start
    assert out == text, "benign run must be left unchanged"
    assert elapsed < 1.0, f"redact() took {elapsed:.2f}s on a 240k credential run"