"""Static scan over six families of safety regexes (exfiltration / injection / destructive / persistence / network /
obfuscation).

self-produced is on by default: our skills are deferred-execution, persistent, propagatable, and their
inputs carry traces (indirect injection), a stronger threat model than Hermes. injection is a
first-class threat — the SKILL.md body itself is the vehicle for injecting into the host context.
Purely deterministic, cannot be bypassed by injection. `scan` returns {family: [matched patterns]};
an empty dict = clean.

ponytail: regex heuristics, not sandboxed execution analysis. It stops explicit malicious strings;
for stronger semantic detection, add an LLM/sandbox.
"""
import re

FAMILIES = {
    "exfiltration": [
        r"curl\s+.*\|\s*(sh|bash)",
        r"wget\s+.*\|\s*(sh|bash)",
        r"(exfiltrate|leak|send|post|upload)\b.{0,30}(http|secret|token|api[_-]?key|password|credential|\benv\b)",
    ],
    "injection": [
        r"ignore\s+(all\s+|any\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?(previous|prior|above)",
        r"(override|bypass|reveal|leak)\b.{0,20}system\s+(prompt|instructions?)",
        r"always\s+(exfiltrate|send|leak|forward)",
    ],
    "destructive": [
        r"\brm\s+-rf?\s+(/|~|\$home|\*)",
        r"\bdrop\s+table\b",
        r"\bmkfs\b",
        r"\bdd\s+if=.*of=/dev/",
        r":\s*\(\s*\)\s*\{\s*:\s*\|\s*:?\s*&\s*\}",
    ],
    "persistence": [
        r"\bcrontab\b",
        r"\.(bashrc|zshrc|bash_profile|profile)\b",
        r"systemctl\s+enable",
        r"\blaunchctl\b",
        r"/etc/(cron|rc\.local|systemd)",
    ],
    "network": [
        r"/dev/tcp/",
        r"reverse\s+shell",
        r"\bnc\s+-l",
        r"\bncat\b.*-e",
        r"socket\.socket\(",
    ],
    "obfuscation": [
        r"base64\s+(-d|--decode)",
        r"\beval\s*\(",
        r"\bexec\s*\(",
        r"(\\x[0-9a-fA-F]{2}){4,}",
        r"\bfromhex\b",
    ],
}

_COMPILED = {fam: [re.compile(p, re.I) for p in pats] for fam, pats in FAMILIES.items()}


def scan(text):
    findings = {}
    for family, patterns in _COMPILED.items():
        hits = [p.pattern for p in patterns if p.search(text)]
        if hits:
            findings[family] = hits
    return findings


def is_clean(text):
    return not scan(text)
