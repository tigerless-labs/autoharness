# E2 — rule-level attribution feasibility

**Question (`DEFINITION.md §8` hard point 1).** "拿自己 5 条真实纠错手验'能否稳定归到
具体规则'。归不准,整条线塌。" Can a real correction be stably attributed to a *specific*
symbol, and does that attribution drive a clean action choice?

**Method.** Detect behavioral corrections in real transcripts (imperative directive, not
question), then hand-attribute each against the actual symbol layer (`lara/CLAUDE.md`,
`autoharness/CLAUDE.md`, project skills). 63 corrections detected across all projects.

## Precondition finding: detection precision gates everything

| Correction detector | precision (sampled) |
|---|---|
| phrase list, any match | ~5% — Chinese interrogatives (还是/为什么/区别/是不是) collide with neg phrases |
| phrase list **minus question markers** | ~50%+ |

The dominant failure mode upstream of attribution is **not** mis-attribution — it is
mis-*detection*: questions read as corrections. **An interrogative-exclusion filter is
mandatory; phrase mining alone is unusable.** (Confirms & sharpens E1.)

## Hand-attribution of real corrections

| # | Real user correction (verbatim, trimmed) | Attributed symbol | Outcome class | Action |
|---|---|---|---|---|
| C14 | "不要有任何废话…一个表给人验证" | CLAUDE.md *"design docs ruthlessly concise, no filler"* | **scope-mismatch** — rule exists but scoped to design docs; correction is about a runbook | broaden scope |
| C15 | "改成完全引用Taxonomy 不要在这里单独阐述 其他地方也一样" | CLAUDE.md *"one authoritative source / cross-reference"* | **in-scope violation** — rule present, not followed | enforce (low adherence) |
| C20 | "不要自己定义没有参考依据的东西" | CLAUDE.md *"verify empirical claims before asserting"* | **in-scope violation** | enforce |
| C13 | "不要打分 在初步idea" | project skill's *no-aggregation* rule | **in-scope violation** | enforce |
| C0 | "不要带语气 就正常回答问题" | — none — | **gap** | candidate add (recurs ×25 sessions) |
| C2 | "不要markdown格式" | — none — | **gap** | candidate add |
| C3 | "写的太多了…其他的 it 都知道" | — none (broad concision) — | **gap / scope-mismatch** | candidate add (recurs ×27) |
| C1 | "commit 不要有 cluade 的标识" | — none — | **gap** | candidate add (recurs ×11) |
| C6 | "不要编造 做不到就不要强行凑" | — none — | **gap** | candidate add (recurs ×24) |

## Findings

1. **Attribution to a specific symbol is feasible** — every correction resolved to either
   a named existing symbol or a confident "no symbol". The make-or-break hard point passes,
   **conditional on** the detection filter above. 归得准。

2. **Attribution is not binary. Three outcome classes, each a different action** — this
   refines the chat-level "violation vs gap" dichotomy:
   - **in-scope violation** (C15, C20, C13): rule exists, applies, ignored → the lever is
     *adherence/enforcement* (hookify · reposition earlier · compress competing noise),
     **not** adding text. Writing another rule the agent already ignores is worthless.
   - **scope-mismatch** (C14, C3): a rule covers a narrower scope than the recurring
     correction → *generalize/broaden* the existing symbol, do not add a sibling.
   - **gap** (C0, C2, C1, C6): no symbol → *candidate addition*, gated by recurrence (§8).

3. **Recurrence (the 增长闸 input) is real and measurable.** The gap themes recur across
   many distinct sessions — tone ×25, verbosity ×27, no-fabrication ×24, markdown ×27,
   commit-signature ×11. A single occurrence must NOT mint a rule; these clear any
   reasonable threshold.

4. **The most striking case is the in-scope violation.** A "ruthlessly concise / no filler"
   rule is *already in CLAUDE.md*, yet verbosity is the single most recurring correction.
   Direct evidence that the bottleneck is **adherence (执行率), not coverage** — the §7 moat.
   More text would not have helped; this rule needed enforcement or repositioning.

## Implications (feed `docs/design/`)

- Detection stage MUST filter interrogatives before anything downstream (cheap, decisive).
- The attribution stage emits one of {in-scope-violation, scope-mismatch, gap}, and the
  action set branches on that class — the dichotomy in the chat answer was too coarse.
- Adherence (did a present, applicable rule get followed?) is a first-class measured
  quantity, not a derived afterthought — it is where the highest-recurrence corrections land.

evidence-for: attribution stage outcome taxonomy; adherence-as-primary-lever; detection
must exclude questions.
