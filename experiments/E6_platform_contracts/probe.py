"""E6 host cross-checks — the host-observable parts of the platform-contract spikes.

S1-S4 and the deny protocol are documented platform contracts (official Claude
Code docs, cited in results.md). This script only reproduces the two facts that
are observable from real transcripts:

  S5 — a used Skill leaves a resolved, namespaced symbolic identity
       (`attributionSkill`, e.g. "plugin:skill").
  S6 — within one user turn the host issues several model API requests
       (distinct `requestId`), so an API-request count != a turn count.

Usage: python3 probe.py [PROJECT_TRANSCRIPT_DIR]
"""
import collections
import json
import sys
from pathlib import Path

DEFAULT_DIR = Path.home() / ".claude/projects/-home-ryan-tigerless-ai-autoharness"


def records(path):
    for line in path.open():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            continue


def main(argv):
    proj = Path(argv[0]) if argv else DEFAULT_DIR
    files = sorted(proj.glob("*.jsonl"))
    assert files, f"no transcripts under {proj}"

    skills = collections.Counter()
    for f in files:
        for o in records(f):
            s = o.get("attributionSkill")
            if s:
                skills[s] += 1
    print(f"[S5] resolved skill identities recorded: {dict(skills.most_common(6))}")
    assert skills, "no attributionSkill records -> skill identity not observable"
    assert any(":" in s for s in skills), "expected at least one namespaced plugin:skill identity"

    worst = (None, 0, 0)
    for f in files:
        recs = list(records(f))
        reqs = {o.get("requestId") for o in recs
                if o.get("type") == "assistant" and o.get("requestId")}
        prompts = sum(1 for o in recs
                      if o.get("type") == "user" and o.get("promptSource") == "user_prompt")
        if len(reqs) > worst[1]:
            worst = (f.name, len(reqs), prompts)
    print(f"[S6] {worst[0]}: {worst[1]} distinct requestId across {worst[2]} user prompt(s) "
          f"-> API requests >> turns")
    assert worst[1] > worst[2], "expected more API requests than user turns"

    print("OK: skill identity is recorded and namespaced (S5); per-turn API-request count "
          ">> turn count, so the rate denominator must be per-turn/Stop, not per request (S6).")


if __name__ == "__main__":
    main(sys.argv[1:])
