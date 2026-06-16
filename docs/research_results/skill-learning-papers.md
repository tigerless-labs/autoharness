# Skill-as-trainable-state paper cluster (2026)

The sibling line to harness optimization: treat the **skill document** as the trainable external state of a frozen agent.

- **SkillOpt** ([arXiv:2605.23904](https://arxiv.org/abs/2605.23904), Microsoft) — first systematic controllable text-space optimizer. Optimizer model turns scored rollouts into bounded add/delete/replace edits on one skill doc; edit accepted only if it **strictly improves a held-out validation score**. Textual learning-rate budget + rejected-edit buffer + slow/meta update. Best/tied on all 52 (model×benchmark×harness) cells; GPT-5.5 +23.5/+24.8/+19.1 pts (chat/Codex/Claude Code); skills transfer across model scales and harnesses. Zero inference-time overhead.
- **SkillGen** ([arXiv:2605.10999](https://arxiv.org/abs/2605.10999)) — key idea: model skills as **interventions** for causal verification — compare same instances with/without the skill, counting both repairs and regressions. Contrastive induction over success+fail trajectories.
- **SkillLens / From Raw Experience to Skill Consumption** ([arXiv:2605.23899](https://arxiv.org/abs/2605.23899)) — full-lifecycle study. Findings: model-generated skills are beneficial on average but show **non-trivial negative transfer**; a strong extractor can be a weak consumer; utility is independent of model scale. (Also the source of the cited "LLM self-eval ≈ 46.4% accuracy" warning.)
- **Trace2Skill** ([arXiv:2603.25158](https://arxiv.org/abs/2603.25158), Qwen) — consolidate parallel trajectories into a skill directory; 35B-derived skills lift a 122B agent up to +57.65pp on WikiTableQuestions; compresses recurring failures into SOPs.
- **EvoSkill** ([arXiv:2603.02766](https://arxiv.org/abs/2603.02766)) — failure-analysis-driven skill evolution; Pareto-frontier selection; zero-shot skill transfer across tasks.
- **MUSE-Autoskill** ([arXiv:2605.27366](https://arxiv.org/abs/2605.27366)) — skill lifecycle management (create/memory/manage/evaluate/refine) + skill-level memory.

**Takeaway:** the methodology is settled — held-out gate (SkillOpt), intervention-style repair-vs-regression (SkillGen), negative-transfer measurement (SkillLens). A harness needs to answer the same question: "is the net effect of adding this positive?", not "how many failures did it fix?"
