# research-loom — 文献→设计 工作区

文献到设计的分层结构在此落地。方法与不变量见 [`../design/research-loom.md`](../design/research-loom.md)，操作指南由 `research-loom` skill 承载。**原子用相对 Markdown 链接互连**（GitHub 可渲染、Obsidian 可反链、可被 `tools/check_doc_links.py` 校验）；`[[ ]]` 不作链接机制。

## 五层 ↔ 子目录

五者是**结构层，非时间步骤**——按需跨层维护、任意顺序、可交错。层间是 provenance 依赖，不是先后。

| 层 | 子目录 | 原子 |
|---|---|---|
| 来源（捕获） | [sources/](sources/index.md) | 文献笔记（一源一卡）。内分 `papers/` `github/` `blogs/` …；类型为开放集，按来源自动归类，无匹配则新建一类。 |
| 方向（组织） | [synthesis/](synthesis/index.md) | 方向 MOC + 概念矩阵 + 我的评判 |
| idea（蒸馏） | [ideas/](ideas/index.md) | 永久笔记（我的话，引用文献） |
| 设计（装配） | [design/](design/index.md) | 设计草稿 + provenance 链 |
| 决策（精炼） | [decisions/](decisions/index.md) | 决策工作表 → ADR |

## Where to start

1. [AutoHarness (Lou et al.)](sources/papers/autoharness-lou.md) — the namesake and its open gap.
2. [Symbolic-Learning Renaissance](sources/blogs/symbolic-learning-renaissance.md) — the thesis tying the corpus together.
3. [Validating harness edits by offline eval runs](synthesis/offline-validation.md) — external benchmark vs. self-bootstrapped replay.
4. [Ecosystem heat & positioning](synthesis/ecosystem-heat.md) — the name collision and the wedge.

**One-line takeaway for autoharness's positioning:** the contested, low-competition gap is *benchmark-free, trajectory-bootstrapped harness evolution with audit/gate/rollback* — distinct from governance frameworks, fuzz-harness generation, and benchmark-requiring optimizers.
