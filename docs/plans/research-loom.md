# 计划 —— research-loom：文献→设计 合成流水线

> 工作产物，豁免设计文档风格规则。分支 `worktree-research-loom`。

## 目标

把"读几十篇论文 → 提炼 → 分方向对比 → 蒸馏成我的 idea → 组装成设计 → 推敲优化定稿"固化成
一条**可维护、可溯源、随想法演化而不重构**的流水线。交付两样：

- **方法**：`research-loom` skill —— 五阶段思路 + "每阶段更新哪个文件、怎么更新"的指南（不存内容、不跑重活）。
- **内容**：`docs/research-loom/` 单一子文件夹 —— 五阶段全部产物。

职责分离遵循"一个事实一个家"：**意图在 `docs/design/`，方法在 skill，内容在 `docs/research-loom/`**。

## 五阶段模型（不变量）

| 阶段 | 子目录 | 原子 | 视图 |
|---|---|---|---|
| ① 捕获 | `1-sources/` | 文献笔记（论点/方法/优缺点） | 卡列表 |
| ② 组织 | `2-directions/` | 方向 MOC | 概念矩阵 + 我的评判列 |
| ③ 蒸馏 | `3-ideas/` | 永久笔记（我的话+引用论文） | idea 看板 |
| ④ 装配 | `4-design/` | 设计草稿 + provenance 链 | C4 脊柱 |
| ⑤ 精炼 | `5-decisions/` | 决策工作表 → ADR | 选项×驱动力矩阵 |

- **三种卡分家**：文献笔记（论文说）≠ 永久笔记（我说）≠ 设计（组装）。
- **provenance 链**：`4-design 的框 → 3-ideas → 1-sources`，任何设计选择可追回论文。
- **④↔⑤ 是循环不是单向**：看图→争议点决策→改图→再看。⑤ 是回灌 ④ 的精炼引擎。
- **append-only**：ADR 只增不删，旧决策标 `superseded-by`。

## 决定（已拍板）

- **D1 = 全搬**：`research_results/{papers,github,blogs}→1-sources`、`synthesis→2-directions`，重写所有 index、全仓链接更新。
- **D2**：`4-design/` = 将来唯一设计家；`docs/design/` 暂冻结为 legacy，过渡期以 `4-design/` 为准。
- **载体**：纯 repo Markdown，Obsidian-ready（frontmatter 装结构化字段、链接用 `[[id]]`、视图与原子分家）。

## 单元（每单元：docs 先行 → 测试 → 代码）

### U1 — 方法设计文档（docs 先行）
- 在 `docs/design/` 新增方法文档（中文）：五阶段不变量、三种卡的 frontmatter 契约、provenance 链规则、`4-design`↔`docs/design` 过渡关系。
- 更新 `docs/design/index.md`。
- 无代码，无测试（纯意图）。

### U2 — 内容区迁移（D1）
- **测试先行** `tests/test_research_loom_migration.py`：
  - 卡数守恒：`count(1-sources) == 旧 count(papers+github+blogs)`；`count(2-directions) ≥ 旧 synthesis 卡数`。
  - 无悬空链接：扫全仓 `[[id]]` 与相对链接，断言每个目标存在。
  - 对抗：注入一条悬空链接 → 校验器必须报错（fail-safe）。
- **代码**：建 `docs/research-loom/` 五层 + `index.md`；迁移文件；重写各 `index.md`；批量改链接。

### U3 — 模板（templates）
- **测试先行**：`tests/test_research_loom_templates.py` 校验五种模板 frontmatter 合规（必填字段、`status` 枚举、`[[ ]]` 占位）。
- **代码**：`.claude/skills/research-loom/templates/` 五卡：`direction-moc / idea-note / design-provenance / decision-worksheet / adr`。

### U4 — Skill 指南
- `.claude/skills/research-loom/SKILL.md`：触发条件 + 五阶段主循环 + 每阶段"更新哪个文件、怎么更新"。
- `references/pipeline.md`（五阶段详解）、`references/note-types.md`（三卡区别 + frontmatter 契约）。
- 跟 `explain-paper` 房规：中文 prose、YAML frontmatter、引用 `docs/research-loom/` 结构。

### U5 — 走通样板（端到端验证）
- 用真实 2–3 篇 `1-sources/` 卡 + 一个方向，实跑 ②③④⑤，产出样例（一张方向矩阵、一条 idea、一段 4-design + provenance、一条决策工作表→ADR）。
- verify：provenance 链从设计可一路追回论文；链接校验器全绿。

### U6 — Sweep & CI
- 扫 `docs/**/index.md`、`docs/TODO.md`、`CLAUDE.md` 的 Key docs 段，补 `research-loom` 入口。
- 开 PR，盯 CI/lint/doc-automation 直到全绿。

## 风险

- **迁移扰动大**：44+ 卡 + 多个 index 改动。缓解：worktree 隔离、链接校验测试当门禁、小步提交。
- **两真相源**：过渡期 `4-design` 与 `docs/design` 并存。缓解：D2 明确"以 `4-design` 为准"，`docs/design` 冻结。

## 待定

- ⑤ 是否改名"决策驱动的精炼"以强调循环（默认保留"精炼"）。
- `matrix.py` 自动矩阵 + Obsidian 视图层 —— 列为后续，本计划不含（纯 Markdown 阶段矩阵手维护）。
