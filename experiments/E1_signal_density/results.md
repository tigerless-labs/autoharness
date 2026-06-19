# E1 — signal-density reality check

**Question.** The thesis (`DEFINITION.md §4`) starts from "收集错误/纠错(error = 用户不满)".
Before designing the harvest stage, measure: *does that signal actually exist at usable
density in real records, and is phrase-matching a viable detector?*

**Method.** `measure_signals.py` over one real user's `~/.claude` (4267 history prompts,
684 sessions with user turns, 17.7k tool calls). Read-only. Three candidate signals.

## Measurements

| Signal | Detector | Density | Eyeballed precision |
|---|---|---|---|
| User correction (flat) | SkillOpt phrase list, `history.jsonl` | **0.1%** of prompts (5/4267) | ~0 (FPs: a question, an index row, a pasted error) |
| User correction (context) | bilingual phrases + assistant→user adjacency, transcripts | **3.3%** of user turns; **11%** of sessions | <30% (interrogatives "要不要/怎么还", pasted errors dominate) |
| **Structural failure** | tool_result `is_error` / error markers in trace | **20.8%** of tool calls; **65%** of sessions | high — an error in tool output is ground truth, not a guess |

## Findings

1. **Phrase-matching for corrections is not viable as the primary channel.** On flat
   prompt text it is 0.1% with near-zero precision; with bilingual phrases and turn
   adjacency it rises to 11% of sessions but precision stays low — questions and pasted
   error text swamp real corrections. This quantifies the doc's hedge (`DECISION.md`:
   "不直接继承关键词判据,太浅") with a number.

2. **The objective structural signal is ~6× denser at the session level (65% vs 11%) and
   far higher precision.** This is the one domain advantage `DEFINITION.md §6` bets on
   ("code 是唯一天然有客观判据") showing up in the raw data.

3. **But raw tool errors are mostly normal exploratory friction, not harness defects**
   (grep misses, file-not-yet-created, first-test-fail-then-pass). 20.8% is the *failure*
   rate, not the *harness-attributable* rate. The attributable subset is much smaller and
   needs an attribution step to isolate (→ E2).

## Design implication (feeds `docs/design/`)

The outcome channel is **two-tier, not user-reply-primary**:

- **Wide net — objective structural failure** (dense, cheap, high-recall): the trace's own
  tool/test/build errors. This is what surfaces *candidate* bad episodes at volume.
- **Sparse high-value overlay — explicit user correction** (rare, but when real it directly
  signals a harness gap, e.g. "为什么还是英文" = an unfollowed preference). Too sparse and
  low-precision for phrase-matching to be the spine; worth an LLM classifier on the
  adjacency-filtered candidates, not a keyword pass.

Corollary: the naive reading "training data = mainly user replies" is **wrong for code
agents**. User replies are the grounding overlay; objective failure is the spine.

evidence-for: harvest stage primary signal = structural failure, not phrase mining.
