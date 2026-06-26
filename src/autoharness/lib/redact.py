"""egress 红线消费者：把 secret/PII 在物化给下游那刻切片脱敏。

规则集是 config 指向的单一来源（redaction_rules.toml，CAP egress + LED 共用）；本模块只
消费、不持有规则。整段匹配替换为 [REDACTED:<category>:<name>]，过度脱敏取安全侧。
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
