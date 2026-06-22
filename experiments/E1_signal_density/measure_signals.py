"""E1 — signal-density measurement over a user's real ~/.claude records.

Quantifies three candidate "the session went badly" signals so the architecture
can choose its primary outcome channel on evidence, not assumption:

  1. user-phrase corrections in history.jsonl   (SkillOpt's heuristic, as-is)
  2. user-phrase corrections in transcripts      (bilingual + turn-adjacency)
  3. structural tool/test/build failures         (objective, in the trace)

Read-only. No network. Prints a table; commit the printed numbers into results.md.
"""
from __future__ import annotations

import glob
import json
import os

NEG_HISTORY = (
    "still broken", "still not", "still wrong", "doesn't work", "does not work",
    "not working", "that's wrong", "thats wrong", "incorrect", " wrong", "no,",
    "nope", "fix it", "didn't", "did not", "broken", "error again", "still failing",
    "still fails", "not fixed", "revert", "undo",
)
POS = ("thanks", "thank you", "perfect", "great", "works now", "fixed",
       "that works", "lgtm", "looks good", "correct")

NEG_EN = ["still broken", "still not", "doesn't work", "does not work", "not working",
          "that's wrong", "thats wrong", "that is wrong", "incorrect", "fix it",
          "didn't work", "did not work", "error again", "still failing", "still fails",
          "not fixed", "revert", "undo", "that broke", "you broke", "no that",
          "not what i", "that's not", "thats not", "wrong ", "actually no", "instead of"]
NEG_ZH = ["还是不行", "不对", "不行", "错了", "没用", "报错", "又错", "还是有问题",
          "不是这", "别这", "不要这", "重新", "为什么还", "怎么还", "没解决", "失败",
          "回滚", "撤销", "改回"]
NEG_TRANSCRIPT = NEG_EN + NEG_ZH

TOOL_ERR_MARKERS = ("error", "exception", "traceback", "failed", "fatal:",
                    "no such file", "command not found", "not found", "cannot",
                    "permission denied", "test failed", "assertionerror",
                    "fail ", "npm err")


def _text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            str(b.get("text", "")) for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def _is_meta(t: str) -> bool:
    return t.startswith("<") or t.startswith("/") or t.startswith("[Pasted")


def measure_history(path: str) -> dict:
    n = neg = pos = meta = 0
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        d = (r.get("display") or "").strip()
        n += 1
        if d.startswith("/") or (d.startswith("<") and d.endswith(">")):
            meta += 1
            continue
        low = d.lower()
        if any(p in low for p in NEG_HISTORY):
            neg += 1
        if any(p in low for p in POS):
            pos += 1
    return {"prompts": n, "meta": meta, "neg": neg, "pos": pos}


def measure_transcripts(root: str) -> dict:
    files = glob.glob(root + "/**/*.jsonl", recursive=True)
    sess = sess_corr = sess_toolerr = 0
    user_turns = corr = adj_corr = tool_uses = tool_errs = 0
    for f in files:
        last_role = None
        saw_turn = saw_tool = had_corr = had_err = False
        try:
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
                content = m.get("content")
                if role == "user":
                    t = _text(content).strip()
                    if t and not _is_meta(t):
                        saw_turn = True
                        user_turns += 1
                        if any(p in t.lower() for p in NEG_TRANSCRIPT):
                            corr += 1
                            had_corr = True
                            if last_role == "assistant":
                                adj_corr += 1
                if isinstance(content, list):
                    for b in content:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "tool_use":
                            tool_uses += 1
                            saw_tool = True
                        if b.get("type") == "tool_result":
                            cont = b.get("content")
                            txt = cont if isinstance(cont, str) else "\n".join(
                                str(x.get("text", "")) for x in cont
                                if isinstance(x, dict)
                            ) if isinstance(cont, list) else ""
                            if b.get("is_error") or any(k in txt.lower() for k in TOOL_ERR_MARKERS):
                                tool_errs += 1
                                had_err = True
                if role in ("user", "assistant"):
                    last_role = role
        except Exception:
            pass
        if saw_turn:
            sess += 1
        if had_corr:
            sess_corr += 1
        if saw_tool and had_err:
            sess_toolerr += 1
    return {
        "sessions": sess, "user_turns": user_turns, "corr": corr,
        "adj_corr": adj_corr, "sess_corr": sess_corr, "tool_uses": tool_uses,
        "tool_errs": tool_errs, "sess_toolerr": sess_toolerr,
    }


if __name__ == "__main__":
    home = os.path.expanduser("~/.claude")
    h = measure_history(os.path.join(home, "history.jsonl"))
    t = measure_transcripts(os.path.join(home, "projects"))
    print("== history.jsonl (phrase, flat) ==")
    print(h, f"neg={100*h['neg']/max(h['prompts'],1):.1f}%")
    print("== transcripts (phrase, bilingual+adjacency) ==")
    print(t)
    print(f"  corr={100*t['corr']/max(t['user_turns'],1):.1f}% of user turns; "
          f"sessions_with_corr={100*t['sess_corr']/max(t['sessions'],1):.0f}%")
    print(f"  tool_err={100*t['tool_errs']/max(t['tool_uses'],1):.1f}% of tool calls; "
          f"sessions_with_tool_err={100*t['sess_toolerr']/max(t['sessions'],1):.0f}%")
