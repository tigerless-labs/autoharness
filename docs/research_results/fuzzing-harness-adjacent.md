# The other "harness": fuzz-driver generation (adjacent reference)

Initially-mistaken branch (2026-06-10). Different from this project's AutoHarness, but
methodologically relevant on **output-quality validation** — kept for reference.

LLM-based fuzz **driver/harness** generation = auto-writing the glue that feeds fuzzers into library APIs. 2026 focus shifted from "can we generate" to **quality assurance & false-positive control** — the same lesson the agent-harness line learned.

- **QuartetFuzz — Quality-Assured Fuzz Harness Generation** ([arXiv:2605.21824](https://arxiv.org/abs/2605.21824)) — most on-point. Four-principles correctness (Logic / API-protocol / Security-boundary / Entry-point) in a generate-check-fix loop before fuzzing. 42 reports, 29 fixed/confirmed (3 CVEs), 4.8% FP; P1/P2 checks intercepted 58 harness-induced false crashes. Code: github.com/OwenSanzas/QuartetFuzz.
- **Agentic Fuzzing** ([arXiv:2605.10074](https://arxiv.org/abs/2605.10074)) — agent reasons directly from a reference bug; names harness engineering as a core challenge. AFuzz on V8: 40 bugs, $35k bounty, 2 CVEs in a month.
- **MASFuzzer** ([arXiv:2604.17977](https://arxiv.org/abs/2604.17977)) — multidimensional API-sequence mining + coverage-guided scheduling; +8.54% coverage; 16 bugs (9 CVEs).
- **Multi-Agent Harness Generation for Java** ([arXiv:2603.08616](https://arxiv.org/abs/2603.08616)) — 5 ReAct agents + on-demand MCP retrieval (no whole-codebase preprocessing); method-targeted coverage; agent-guided termination; ~$3.20/10min per harness.
- **STITCH** ([arXiv:2602.18689](https://arxiv.org/abs/2602.18689)) — runtime-assembled API "blocks" instead of synthesis-time fixed sequences; 70% precision vs 12% next-best; 131 new bugs across 102 projects.
- **HarnessAgent** ([arXiv:2512.03420](https://arxiv.org/abs/2512.03420)), **FalseCrashReducer** ([arXiv:2510.02185](https://arxiv.org/abs/2510.02185), directly about OSS-Fuzz-Gen false positives eroding maintainer trust), **Scheduzz** ([arXiv:2507.18289](https://arxiv.org/abs/2507.18289)).

**Cross-line lesson:** both communities converged on "automatic triage/verification is mandatory, not optional" — generating candidates is cheap; not flooding the recipient with noise is the hard, valuable part. Mirrors the OSS "strip mining" backlash (HN: metabase.com/blog/strip-mining-era-of-open-source-security).
