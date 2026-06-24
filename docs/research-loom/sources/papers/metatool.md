# [论文] MetaTool: Deciding Whether to Use Tools and Which to Use

**Yue Huang, Jiawen Shi, Yuan Li, … Lichao Sun** — [arXiv:2310.03128](https://arxiv.org/abs/2310.03128) (v6, 2024-12; submitted 2023-10) · ICLR 2024 · code: [HowieHwong/MetaTool](https://github.com/HowieHwong/MetaTool).

The academic formalization of the **"should this capability fire here?"** question. Splits the decision into two measurable capabilities: **tool-usage awareness** (is a tool needed at all) and **tool selection** (which one). Ships **ToolE**, a query dataset (single- + multi-tool), with four selection subtasks: similar-choice, scenario-specific, reliability-issue, multi-tool.

Headline over 8 LLMs: **most still struggle to select tools correctly** — a measured gap between LLMs and "genuine agents." Developer takeaway: pick an appropriate rewrite model to **regenerate tool descriptions** for the downstream LLM (i.e. the description is the routing lever).

**Relevance to autoharness:** the closest *peer-reviewed proxy* for skill-recall — a skill firing when relevant is exactly "usage awareness + selection," just measured on a labeled tool benchmark rather than on Claude Code. Confirms the failure is real and **description-bound**. Feeds [synthesis/skill-recall-execution](../../synthesis/skill-recall-execution.md); proxy-not-direct caveat noted there.
