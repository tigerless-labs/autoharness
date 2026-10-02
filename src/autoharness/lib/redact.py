"""egress redline consumer: redacts secret/PII slices at the moment they are materialized downstream.

The rule set is the single source pointed to by config (redaction_rules.toml, shared by CAP egress +
LED); this module only consumes rules, it does not own them. Each match is replaced wholesale with
[REDACTED:<category>:<name>], erring on the side of over-redaction for safety. A rule may set
`validate = "<name>"` to gate its regex matches through a named checker here (e.g. luhn for
credit_card), keeping sequences that fail the check in the stream as evidence.
"""
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


def _replacer(category, name, validator):
    token = f"[REDACTED:{category}:{name}]"
    if validator is None:
        return token

    def _replace(match):
        return token if validator(match.group(0)) else match.group(0)

    return _replace


def redact(text, rules_path=None):
    out = text
    key = str(rules_path) if rules_path else str(config.REDACTION_RULES)
    for category, name, rx, validator in _rules(key):
        out = rx.sub(_replacer(category, name, validator), out)
    return out


def secret_hits(text, rules_path=None):
    """Names of the secret rules *text* matches — a gate, not a rewrite (PII stays redact-only)."""
    return [name for category, name, rx in _rules(rules_path)
            if category == "secret" and rx.search(text)]
