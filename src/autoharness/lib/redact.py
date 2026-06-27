"""egress redline consumer: redacts secret/PII slices at the moment they are materialized downstream.

The rule set is the single source pointed to by config (redaction_rules.toml, shared by CAP egress +
LED); this module only consumes rules, it does not own them. Each match is replaced wholesale with
[REDACTED:<category>:<name>], erring on the side of over-redaction for safety.
"""
import functools
import re
import tomllib
from pathlib import Path

from autoharness import config


@functools.lru_cache(maxsize=4)
def _rules(rules_path):
    path = Path(rules_path) if rules_path else config.REDACTION_RULES
    data = tomllib.loads(path.read_text())
    compiled = []
    for category in ("secret", "pii"):
        for rule in data.get(category, []):
            compiled.append((category, rule["name"], re.compile(rule["pattern"])))
    return compiled


def redact(text, rules_path=None):
    out = text
    for category, name, rx in _rules(rules_path):
        out = rx.sub(f"[REDACTED:{category}:{name}]", out)
    return out
