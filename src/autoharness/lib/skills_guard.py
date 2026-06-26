"""六族安全正则静态扫描（exfiltration / injection / destructive / persistence / network /
obfuscation）。

self-produced 默认开：我们的 skill 延迟执行、持久、可传播、来料含 trace（间接注入），威胁
模型强于 Hermes。injection 一等威胁 —— SKILL.md 正文本身即注入宿主上下文的载体。纯确定性、
不可注入绕过。`scan` 返回 {family: [命中的 pattern]}；空 dict = 干净。

ponytail: 正则启发式、非沙箱执行分析。挡的是显式恶意串；要更强的语义检测再上 LLM/sandbox。
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
