"""E3 — applicability / omission tractability probe (DEFINITION.md §7 造0, the 共同盲区).

Omission = "a symbol should have fired but didn't". Decompose into:
    执行率 (adherence) = fired_and_applicable / applicable
The numerator's "fired" is observable for SKILLS (invocation is a fact in the
trace); the denominator "applicable" is a semantic judgement. This probe maps
which half is structurally tractable without an LLM, on real data.

Three measurements:
  1. skill dormancy        — distinct skills invoked vs available (numerator side)
  2. rule-adherence proxy  — worktree/TDD usage rate, to expose the denominator trap
  3. objective adherence   — Claude commit-signature persistence vs a recurring
     user correction (the one case fully measurable with zero LLM)
Read-only except (3) shells out to `git log` on sibling repos.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess


def _text(c) -> str:
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return " ".join(str(b.get("text", "")) for b in c
                        if isinstance(b, dict) and b.get("type") == "text")
    return ""


def skill_and_adherence(root: str) -> None:
    skill_calls: dict = {}
    sess = wt = test = code = 0
    for f in glob.glob(root + "/**/*.jsonl", recursive=True):
        saw = used_wt = wrote_test = wrote_code = False
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
            c = m.get("content")
            if isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict) or b.get("type") != "tool_use":
                        continue
                    saw = True
                    nm, inp = b.get("name", ""), b.get("input", {}) or {}
                    if nm == "Skill":
                        s = inp.get("skill") or inp.get("command") or "?"
                        skill_calls[s] = skill_calls.get(s, 0) + 1
                    if "worktree" in json.dumps(inp).lower():
                        used_wt = True
                    if nm in ("Write", "Edit"):
                        p = str(inp.get("file_path", ""))
                        if re.search(r"test_.*\.py$|/tests?/|\.test\.|\.spec\.", p):
                            wrote_test = True
                        elif p.endswith((".py", ".ts", ".tsx", ".js", ".go", ".rs")):
                            wrote_code = True
        if saw:
            sess += 1
            wt += used_wt
            test += wrote_test
            code += wrote_code
    print(f"distinct skills ever invoked: {len(skill_calls)}  {dict(sorted(skill_calls.items(), key=lambda x:-x[1]))}")
    print(f"sessions(tool)={sess}  worktree={wt} ({100*wt//max(sess,1)}%)  "
          f"test={test} ({100*test//max(sess,1)}%)  code={code} ({100*code//max(sess,1)}%)")
    print("  -> raw adherence % is uninterpretable: denominator (applicable sessions) unknown")


def signature_adherence(projects_root: str, repos: list) -> None:
    print("\nClaude commit-signature persistence (objective, zero-LLM):")
    for d in repos:
        path = os.path.join(projects_root, d)
        if not os.path.isdir(os.path.join(path, ".git")):
            continue
        bodies = subprocess.run(
            ["git", "-C", path, "log", "-200", "--format=%b"],
            capture_output=True, text=True).stdout
        sig = len(re.findall(r"(?i)co-authored-by: claude|generated with.*claude", bodies))
        n = len(subprocess.run(["git", "-C", path, "log", "--oneline", "-200"],
                               capture_output=True, text=True).stdout.splitlines())
        print(f"  {d:16s} {sig}/{n} signed")


if __name__ == "__main__":
    skill_and_adherence(os.path.expanduser("~/.claude/projects"))
    signature_adherence(os.path.expanduser("~/tigerless_ai"),
                        ["lara", "livins", "context-xray", "cost-xray",
                         "ai_translation", "harness-tax", "autoharness"])
