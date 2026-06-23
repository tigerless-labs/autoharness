# [论文] HASP: Harnessing LLM Agents with Skill Programs

**Hongjun Liu, Yifei Ming, Shafiq Joty, Chen Zhao** (NYU · Salesforce AI Research) — [arXiv:2605.17734](https://arxiv.org/abs/2605.17734) · 2026-05-18.

> The skill+harness title collision: this is the paper most likely meant by "skillharness." Distinct from [AutoHarness](autoharness-lou.md) and from this project (see [[autoharness-means-agent-harness]]).

Skills become **Program Functions (PFs)** — executable modules, not advisory text. Each PF is `should_activate` (fires on a failure-prone state) + `intervene` (returns the repair). The harness is an external control layer: base policy proposes an action → harness retrieves PFs → evaluates activation → runs intervention (**MODIFY_ACTION** rewrites the next action, **INJECT_CONTEXT** appends corrective text, else **NOOP**) → revised action goes back. PFs are mined from training-pool failures and admitted only after syntax + interface + mock-execution validation. One interface, three uses: inference-time intervention, post-training supervision, self-improving library evolution.

**Numbers.** Web-search: PF-only 51.0% → on-policy distillation 62.5%; HASP-Evolve+RS 60.3% vs Search-R1 29.9% (+30.4). Math 35.9→45.4. Coding pass@1 ~69.9. Interventions split 65.1% action-level / 34.9% context-level. Ablating the four evolution signals (timing/mode/correctness/outcome) costs 7.8/15.5/12.1/12.8 pts; **unfiltered evolution collapses to 36.3% vs 60.3% filtered.**

**Referenced directions (their Related Work).**
- **A. Post-training / RL for agent reasoning & tool use** — Search-R1, ReSearch, ZeroSearch, StepSearch, VerlTool; SimpleRL-zoo, Open-Reasoner-Zero, General-Reasoner, ToRL, AceCoder, P-GRPO. HASP frames itself as modular across SFT / rejection-sampling / on-policy-distillation rather than one RL paradigm.
- **B. Skill-augmented & self-improving agents** — [ReAct], Toolformer, AutoGen, AgentFlow; [Reflexion](reflexion.md), ExpeL, [Voyager](voyager.md); MemSkill, SkillRL, EvolveR, [SAGE](sage.md). Contrast they draw: prior work reuses experience as **prompt text or task routines**; HASP uses **executable state→action intervention functions**.
- **Table 1 axes** (Form / Runtime-control / Learning-signal / Policy-training / Skill-evolution): HASP claims it is the only one full on all five — its wedge is **runtime control** (others partial) + **skill evolution** (absent from pure-RL).

**Relevance to autoharness.** HASP is the *opposite design corner* on the axis that defines us, which makes it the sharpest contrast point:
- **Executable + auto-written + weight-training** vs our **text-layer, never-auto-write, frozen-model** stance. HASP writes/admits code and trains the policy; we treat human adoption as structural grounding (invariant 1) and stay text-space like [SkillOpt](skillopt.md), opposite to the [TMEM](tmem.md) weight corner.
- Their PF `should_activate` predicate is the executable form of our **applicability gate** (invariant 6 — omission needs applicability before it's a verdict).
- Their unfiltered-evolution collapse (36.3 vs 60.3) and per-signal ablations are external evidence for our **gate-or-collapse** posture (invariants 7–8) — file the collapse datapoint alongside [APEX](apex.md).
- Action-vs-context intervention split mirrors our **attribution→lever** mapping (enforce / generalize / retire / gated-add), but HASP picks the lever to *act automatically*; we pick it to *propose to a human*.
- Direction A (RL post-training) is orthogonal-to-counter to us (weight-free); Direction B is where our corpus overlaps — Reflexion / Voyager / SAGE already carded; MemSkill / SkillRL / EvolveR / ExpeL / AgentFlow are gaps.
