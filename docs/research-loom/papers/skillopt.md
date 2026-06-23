# [论文] SkillOpt: Executive Strategy for Self-Evolving Agent Skills

**Microsoft** — [arXiv:2605.23904](https://arxiv.org/abs/2605.23904) · 2026-05 · code: [microsoft/SkillOpt](https://github.com/microsoft/SkillOpt) (~5,640★). See also the [SkillOpt-Sleep](../github/microsoft-skillopt-sleep.md) bootstrap-validation plugin.

First systematic controllable **text-space optimizer**. An optimizer model turns scored rollouts into bounded add/delete/replace edits on one skill doc; an edit is accepted only if it **strictly improves a held-out validation score**. Textual learning-rate budget + rejected-edit buffer + slow/meta update.

Best or tied on all 52 (model × benchmark × harness) cells; GPT-5.5 +23.5/+24.8/+19.1 pts (chat / Codex / Claude Code); skills transfer across model scales and harnesses; zero inference-time overhead.

**Relevance to autoharness:** the canonical **held-out-gate** discipline and the engineering skeleton autoharness builds on. "Gradient descent in symbol space": rollout = forward, reflection = backward, held-out gate = validation (cf. the [symbolic-learning thesis](../blogs/symbolic-learning-renaissance.md)).
