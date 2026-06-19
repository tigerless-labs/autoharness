# E3 — applicability / omission tractability

**Question (`DEFINITION.md §7` 造0, the 共同盲区).** Omission = "a symbol should have fired
but didn't". Can we detect it? The named moat is 适用性推断 — the *denominator* of
执行率 = fired_and_applicable / applicable.

## Measurements

1. **Skill firing is observable; most skills are dormant.** Only **6 distinct skills** were
   ever invoked via the Skill tool across 653 tool-using sessions (top: last30days ×12,
   claude-api ×6). Dozens of available skills fired zero times.

2. **Raw adherence proxies are uninterpretable.** Worktree usage 6% of sessions, test-file
   writes 6%, in projects that *mandate* worktree-per-task + TDD. This is **not** 94%
   violation: most sessions are Q&A/exploration (see E2) where those rules don't apply. The
   raw rate without the applicability denominator is **meaningless** — and computing the
   denominator ("was this a non-trivial code change in a mandating project?") is a semantic
   judgement.

3. **One gap is fully objective.** "commit 不要有 claude 的标识" (E2 C1, recurs ×11 sessions)
   is measurable with `git log` alone — no LLM:

   | repo | signed / last-200 |
   |---|---|
   | lara | 86/121 | livins | 83/200 | context-xray | 35/44 |
   | cost-xray | 13/21 | ai_translation | 11/13 | harness-tax | 9/15 |

   ~70% persistence **including this experiment's own commits**.

## Findings

1. **Omission factorizes into observable × semantic.** "Did it fire?" is structurally
   observable for *skills* (invocation is a trace fact), fuzzy for *prose rules* (always
   in-context, so "fired" ≠ "followed"). "Should it have?" (applicability) is semantic for
   both. **The moat's denominator is the genuinely hard half** — confirmed, not solved.

2. **v1/v2 split falls straight out of this.** Without an LLM you can surface *dormant
   skills* and *raw proxies* as **review candidates** — never as confident omission verdicts
   (the denominator is missing). True omission detection (per-(symbol,session) applicability)
   needs the v2 LLM judge. This matches §8 "v1 给动作建议+证据,不给精确分数".

3. **The signature case is the canonical worked example for the whole system** — and it is
   richer than "gap":
   - The agent signs because an **explicit harness instruction tells it to** ("End git
     commit messages with: Co-Authored-By: Claude…"). So this is **not** an adherence slip —
     it is a **harness symbol actively producing a user-rejected behavior** = `DEFINITION §2`
     "符号污染决策", the thesis in one case.
   - Attribution target = that instruction symbol; correct action = **retire/override it**
     (or hookify the user's preference so it wins), not add a rule.
   - Gate = `grep` git log before/after. **Zero-oracle, zero-LLM verification** — exactly the
     "flaw 出现率降没降" verify the docs prize, available for free here.

## Implication

- v1 acts only where firing/adherence is **objectively observable** (skill invocation counts,
  git-checkable behaviors like the signature, presence/dedup/token cost). It presents
  everything else as review candidates.
- v2 adds the applicability estimator (LLM per-(symbol,session)) that turns raw adherence
  proxies into real 执行率, unlocking prose-rule omission.
- Feature the **commit-signature conflict** as the design's worked example end-to-end.

evidence-for: v1 = objectively-observable actions only; applicability estimator is v2;
conflict (symbol-vs-user) is a first-class attribution outcome alongside violation/gap.
