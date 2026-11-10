"""Vendor-prefixed keys are redacted when they appear bare, and secret-named variables lose their value.

The values are generated from a fixed seed at run time, so no token-shaped literal lands in the repository.
"""
import random
import string

import pytest

from autoharness.lib import redact

_AL = string.ascii_letters + string.digits
_B64U = _AL + "-_"
_rnd = random.Random(20261023)


def _rs(n, alphabet=_AL):
    return "".join(_rnd.choice(alphabet) for _ in range(n))


_KEYS = {
    "stripe_key": "sk_live_" + _rs(24),
    "anthropic_api_key": "sk-ant-api03-" + _rs(93, _B64U) + "AA",
    "openai_api_key": "sk-" + _rs(48),
    "google_api_key": "AIza" + _rs(35, _B64U),
    "npm_token": "npm_" + _rs(36),
    "jwt": "eyJ" + _rs(34, _B64U) + ".eyJ" + _rs(70, _B64U) + "." + _rs(43, _B64U),
}


@pytest.mark.parametrize("rule", sorted(_KEYS))
def test_bare_vendor_key_is_redacted_in_prose_and_in_a_log(rule):
    key = _KEYS[rule]
    for text, rest in (
        (f"Here is the thing I pasted earlier: {key} and then I moved on.", "and then I moved on."),
        (f"$ ./deploy.sh\nstarting...\n{key}\nexit 0\n", "exit 0"),
    ):
        out = redact.redact(text)
        assert key not in out
        assert f"[REDACTED:secret:{rule}]" in out
        assert rest in out


@pytest.mark.parametrize("rule", sorted(_KEYS))
def test_vendor_key_assigned_to_a_variable_is_still_redacted(rule):
    key = _KEYS[rule]
    for text in (f"export SOME_VALUE={key}", '{"some_value": "' + key + '", "ok": true}'):
        assert key not in redact.redact(text)


@pytest.mark.parametrize("name", ["AWS_SECRET_ACCESS_KEY", "STRIPE_SECRET_KEY", "secret_key", "SECRET-KEY"])
def test_secret_named_variable_keeps_no_value(name):
    value = _rs(40, _AL + "+/")
    for text in (f"export {name}={value}", '{"' + name.lower() + '": "' + value + '"}', f"{name}: {value}"):
        assert value not in redact.redact(text)


@pytest.mark.parametrize(
    "url",
    [
        "postgres://app:P@ss!w0rd#2026/ab@db.internal:5432/prod",
        "mysql+pymysql://service:p%40ss%2Fword@db.internal/app",
        "https://deploy:temporary-password@example.com/artifact",
        "https://deploy:temporary-password@example.com,",
    ],
)
def test_url_credentials_are_redacted_as_a_unit(url):
    out = redact.redact(url)
    assert "://" not in out
    assert "[REDACTED:secret:url_credentials]" in out
    assert out.endswith(("db.internal:5432/prod", "db.internal/app", "example.com/artifact", "example.com,"))


@pytest.mark.parametrize(
    "url",
    [
        "postgres://db.internal:5432/prod",
        "https://example.com/artifact",
    ],
)
def test_urls_without_embedded_credentials_are_left_alone(url):
    assert redact.redact(url) == url


def test_at_sign_in_url_path_is_not_treated_as_embedded_credentials():
    out = redact.redact("https://example.com/path@other.example")
    assert "[REDACTED:secret:url_credentials]" not in out


@pytest.mark.parametrize(
    "text",
    [
        "the risk-management-and-compliance-framework-overview was updated",
        "task-force-coordination-and-escalation-procedures-for-q4 were agreed",
        "disk-usage-report-for-the-staging-and-production-clusters is ready",
        "ask-the-team-about-the-quarterly-planning-session-notes",
        "the secret key to a good review is small diffs",
        "npm_config_registry is set",
        "see AIzaSomething for details",
        "a.b.c and eyJ are not tokens",
    ],
)
def test_ordinary_text_is_left_alone(text):
    assert redact.redact(text) == text
