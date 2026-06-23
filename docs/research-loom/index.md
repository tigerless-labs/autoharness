# research-loom — 文献→设计 工作区

文献到设计的合成流水线在此落地。方法与不变量见 [`../design/research-loom.md`](../design/research-loom.md)，操作指南由 `research-loom` skill 承载。**原子用相对 Markdown 链接互连**（GitHub 可渲染、Obsidian 可反链、可被 `tools/check_doc_links.py` 校验）；`[[ ]]` 不作链接机制。

## 五阶段 ↔ 子目录

| 阶段 | 子目录 | 原子 |
|---|---|---|
| ① 捕获 | `papers/` `github/` `blogs/` … | 文献笔记（一源一卡）。类型为开放集，捕获时按来源自动归类，无匹配则新建一类。 |
| ② 组织 | [synthesis/](synthesis/index.md) | 方向 MOC + 概念矩阵 + 我的评判 |
| ③ 蒸馏 | [ideas/](ideas/index.md) | 永久笔记（我的话，引用文献） |
| ④ 装配 | [design/](design/index.md) | 设计草稿 + provenance 链 |
| ⑤ 精炼 | [decisions/](decisions/index.md) | 决策工作表 → ADR |

## 来源库（① 捕获）

**One source = one card**；标题标注 `[论文]` / `[GitHub]` / `[博客]`，命名作品与作者/机构，链接出处，并附与 autoharness 的相关性。研究笔记，`docs/design/` 风格规则不适用。

- **[papers/](papers/index.md)** — `[论文]` cards (49), grouped: core harness line · skill-as-state · retrieval/selection · self-evolving memory · surveys/infra · foundational · fuzzing-adjacent.
- **[github/](github/index.md)** — `[GitHub]` cards for non-paper-code repos: OSS agents, skill packs, the three "AutoHarness" name-collisions, trending projects (+ official-implementation index).
- **[blogs/](blogs/index.md)** — `[博客]` cards: the symbolic-learning thesis, Heuristic Learning, the Claude Code skills blog, the 1k-experiments log.
- **[synthesis/](synthesis/index.md)** — ② 组织：the cross-source analysis no single card owns: the [benchmark-free validation spectrum](synthesis/benchmark-free-validation.md) and [ecosystem heat / positioning](synthesis/ecosystem-heat.md).

## Where to start

1. [AutoHarness (Lou et al.)](papers/autoharness-lou.md) — the namesake and its open gap.
2. [Symbolic-Learning Renaissance](blogs/symbolic-learning-renaissance.md) — the thesis tying the corpus together.
3. [Defining harness quality without a benchmark](synthesis/benchmark-free-validation.md) — how to gate edits with no oracle.
4. [Ecosystem heat & positioning](synthesis/ecosystem-heat.md) — the name collision and the wedge.

**One-line takeaway for autoharness's positioning:** the contested, low-competition gap is *benchmark-free, trajectory-bootstrapped harness evolution with audit/gate/rollback* — distinct from governance frameworks, fuzz-harness generation, and benchmark-requiring optimizers.
