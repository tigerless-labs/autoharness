"""egress redline consumer: redacts secret/PII slices at the moment they are materialized downstream.

The rule set is the single source pointed to by config (redaction_rules.toml, shared by CAP egress +
LED); this module only consumes rules, it does not own them. Each match is replaced wholesale with
[REDACTED:<category>:<name>], erring on the side of over-redaction for safety. A rule may set
`validate = "<name>"` to gate its regex matches through a named checker here (e.g. luhn for
credit_card), keeping sequences that fail the check in the stream as evidence.
"""
import bisect
import functools
import re
import tomllib
from pathlib import Path

from autoharness import config


def _passes_luhn(text):
    digits = re.sub(r"\D", "", text)
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


_VALIDATORS = {"luhn": _passes_luhn}


@functools.lru_cache(maxsize=4)
def _rules(rules_path):
    path = Path(rules_path) if rules_path else config.REDACTION_RULES
    data = tomllib.loads(path.read_text())
    compiled = []
    for category in ("secret", "pii"):
        for rule in data.get(category, []):
            validate = rule.get("validate")
            if validate is not None and validate not in _VALIDATORS:
                raise ValueError(
                    f"unknown validator {validate!r} on rule {category}.{rule['name']}"
                )
            compiled.append(
                (category, rule["name"], re.compile(rule["pattern"]), _VALIDATORS.get(validate))
            )
    return compiled


@functools.lru_cache(maxsize=4)
def _placeholders(rules_path):
    # rules run one after another over the rewritten text, so a later rule sees earlier placeholders
    # (and a second pass the first one's): `secret:bearer_token` would read as an api_key_assignment.
    # Only this rule set's own names: a made-up `[REDACTED:secret:<a real key>]` is still raw text.
    names = "|".join(re.escape(f"{category}:{name}") for category, name, _, _ in _rules(rules_path))
    return re.compile(rf"\[REDACTED:(?:{names})\]")


def _inside(text, rules_path):
    """Predicate: does a match lie entirely inside one of this rule set's placeholders in *text*?"""
    spans = [m.span() for m in _placeholders(rules_path).finditer(text)]
    starts = [start for start, _ in spans]

    def inside(match):
        i = bisect.bisect_right(starts, match.start()) - 1  # placeholders never overlap: one candidate
        return i >= 0 and match.end() <= spans[i][1]

    return inside


def _replacer(category, name, validator, inside):
    token = f"[REDACTED:{category}:{name}]"

    def _replace(match):
        if inside(match):
            return match.group(0)  # an existing placeholder is not raw text
        if validator is not None and not validator(match.group(0)):
            return match.group(0)
        return token

    return _replace


def redact(text, rules_path=None):
    out = text
    key = str(rules_path) if rules_path else str(config.REDACTION_RULES)
    for category, name, rx, validator in _rules(key):
        out = rx.sub(_replacer(category, name, validator, _inside(out, key)), out)
    return out


def secret_hits(text, rules_path=None):
    """Names of the secret rules *text* matches — a gate, not a rewrite (PII stays redact-only)."""
    key = str(rules_path) if rules_path else str(config.REDACTION_RULES)
    inside = _inside(text, key)  # quoting an already-redacted window is not leaking a secret
    return [
        name
        for category, name, rx, validator in _rules(key)
        if category == "secret"
        and any(not inside(match) and (validator is None or validator(match.group(0)))
                for match in rx.finditer(text))
    ]
