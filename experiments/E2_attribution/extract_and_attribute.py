"""E2 — rule-level attribution feasibility (DEFINITION.md §8 hard point 1).

Two stages over real transcripts:
  1. detect behavioral corrections — imperative directives, NOT questions
     (the interrogative-exclusion filter is the precision lever E1/E2 found).
  2. theme recurrence — count how often each correction theme recurs across
     distinct sessions (the 增长闸 recurrence test needs real numbers).

Hand-attribution of the detected corrections to specific CLAUDE.md symbols is
recorded in results.md (a human judgement step, not automated here).
Read-only.
"""
from __future__ import annotations

import glob
import json
import os

CORR_MARKERS = ["不要", "别用", "别再", "不是这", "不应该", "应该先", "下次", "记住",
                "以后", "always", "never", "don't", "do not", "stop ", "你应该",
                "你不该", "不用", "错了", "写错", "搞错"]
QUESTION_MARKERS = ["吗", "呢", "区别", "怎么", "为什么", "是不是", "究竟", "?", "？",
                    "哪个", "几个", "多少", "如何", "what", "how ", "why ", "which"]

THEMES = {
    "verbosity/fluff": ["废话", "太多了", "太长", "简洁", "精简", "不用教", "啰嗦",
                        "冗长", "too long", "too verbose", "more concise"],
    "format/markdown": ["markdown", "不要格式", "plain text", "纯文本", "别用markdown"],
    "tone/persona": ["不要带语气", "正常回答", "别夸", "客观", "tone", "语气"],
    "no-fabrication": ["不要编造", "别编", "不要强行", "没有依据", "没有参考", "凭空",
                       "胡编", "made up", "fabricat"],
    "claude-signature": ["cluade的标识", "claude的标识", "co-author", "claude标识",
                         "别带claude", "签名", "signature"],
    "dont-duplicate": ["完全引用", "不要单独阐述", "不要重复", "交叉引用",
                       "其他地方也一样", "cross-reference", "don't duplicate"],
}


def _text(c) -> str:
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "\n".join(str(b.get("text", "")) for b in c
                         if isinstance(b, dict) and b.get("type") == "text")
    return ""


def _is_correction(t: str) -> bool:
    low = t.lower()
    if not any(p in low for p in CORR_MARKERS):
        return False
    has_q = any(q in t for q in QUESTION_MARKERS)
    has_imperative = ("不要" in t or "别" in t or "don't" in low or "do not" in low)
    return has_imperative or not has_q


def run(root: str) -> None:
    files = glob.glob(root + "/**/*.jsonl", recursive=True)
    corrections = []
    theme_turns = {k: 0 for k in THEMES}
    theme_sess = {k: set() for k in THEMES}
    for f in files:
        sid = os.path.basename(f)
        prev = ""
        for line in open(f, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            m = r.get("message")
            if not isinstance(m, dict):
                continue
            role = m.get("role")
            t = _text(m.get("content")).strip()
            if role == "assistant" and t:
                prev = t
            elif role == "user" and t and not (t.startswith("<") or t.startswith("/")
                                               or t.startswith("[Pasted")):
                if _is_correction(t) and len(t) < 240 and prev:
                    corrections.append((sid, prev[-160:], t[:230]))
                for k, phr in THEMES.items():
                    if any(p.lower() in t.lower() for p in phr) and _is_correction(t):
                        theme_turns[k] += 1
                        theme_sess[k].add(sid)
                prev = ""
    print(f"behavioral corrections detected: {len(corrections)}")
    print("\ntheme                 turns  distinct_sessions")
    for k in THEMES:
        print(f"  {k:18s}  {theme_turns[k]:4d}   {len(theme_sess[k])}")


if __name__ == "__main__":
    run(os.path.expanduser("~/.claude/projects"))
