"""egress redline consumer: redacts secret/PII slices at the moment they are materialized downstream.

The rule set is the single source pointed to by config (redaction_rules.toml, shared by CAP egress +
LED); this module only consumes rules, it does not own them. Each match is replaced wholesale with
[REDACTED:<category>:<name>], erring on the side of over-redaction for safety. A rule may set
`validate = "<name>"` to gate its regex matches through a named checker here (e.g. luhn for
credit_card), keeping sequences that fail the check in the stream as evidence.

Rules are collected against the original text and applied in one pass, so no rule ever sees another
rule's placeholder: the placeholder is the only record of what was removed, and a sequential sweep
let a later rule (api_key_assignment) match the `secret:<name>` inside an earlier rule's placeholder
and rewrite it as a nested, generic one. Overlapping matches merge into one span named by the earliest
rule in the file: no match is ever dropped, or the part of it no other rule covered would stay raw.
Placeholders already in the input are not rematched: redacted text is fed back in (capture redacts the
window, the promoter redacts the evidence quoted from it again).
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


def _token(category, name):
    return f"[REDACTED:{category}:{name}]"


@functools.lru_cache(maxsize=4)
def _placeholder(key):
    # only this rule set's own tokens: a made-up `[REDACTED:secret:<a real key>]` is still raw text
    return re.compile("|".join(re.escape(_token(category, name)) for category, name, _, _ in _rules(key)))


def _raw(text, key):
    """Predicate: is a match raw text, not lying wholly inside one of this rule set's placeholders?
    A match that reaches outside one (a key block around a redacted Comment line) is raw."""
    held = [match.span() for match in _placeholder(key).finditer(text)]
    starts = [start for start, _ in held]

    def raw(match):
        i = bisect.bisect_right(starts, match.start()) - 1  # placeholders never overlap: one candidate
        return i < 0 or match.end() > held[i][1]

    return raw


def _kept(rx, validator, text):
    """Matches of *rx* in *text* that the rule's validator keeps, overlapping ones included: the search
    resumes one character on, not after the match. finditer skipped a card right after a phone number
    (one digit run whose first window fails luhn), and resuming after a kept window that happens to pass
    luhn would skip the rest of a real card it overlaps; overlapping kept matches merge into one span."""
    if validator is None:
        yield from rx.finditer(text)
        return
    pos = 0
    while (match := rx.search(text, pos)) is not None:
        if validator(match.group(0)):
            yield match
        pos = match.start() + 1


def _spans(text, key):
    """Disjoint [start, end, rank, token] spans covering every rule match in *text*, in order. A match
    that overlaps another extends its span instead of being dropped: a key block whose Comment line held
    an AWS key id kept its whole body when the block lost to the earlier aws rule."""
    raw = _raw(text, key)
    found = sorted(
        (match.start(), match.end(), rank, _token(category, name))
        for rank, (category, name, rx, validator) in enumerate(_rules(key))
        for match in _kept(rx, validator, text)
        if raw(match)
    )
    spans = []
    for start, end, rank, token in found:
        if spans and start < spans[-1][1]:
            last = spans[-1]
            last[1] = max(last[1], end)
            if rank < last[2]:
                last[2:] = [rank, token]
        else:
            spans.append([start, end, rank, token])
    return spans


def redact(text, rules_path=None):
    key = str(rules_path) if rules_path else str(config.REDACTION_RULES)
    out = []
    cursor = 0
    for start, end, _, token in _spans(text, key):
        out.append(text[cursor:start])
        out.append(token)
        cursor = end
    out.append(text[cursor:])
    return "".join(out)


def secret_hits(text, rules_path=None):
    """Names of the secret rules *text* matches — a gate, not a rewrite (PII stays redact-only)."""
    key = str(rules_path) if rules_path else str(config.REDACTION_RULES)
    raw = _raw(text, key)
    return [
        name
        for category, name, rx, validator in _rules(key)
        if category == "secret"
        and any(raw(match) for match in _kept(rx, validator, text))
    ]
