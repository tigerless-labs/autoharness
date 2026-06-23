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
| ① 捕获 | `papers/` `github/` `blogs/` … | 文献笔记（论点/方法/优缺点） | 卡列表 |
| ② 组织 | `synthesis/` | 方向 MOC | 概念矩阵 + 我的评判列 |
| ③ 蒸馏 | `ideas/` | 永久笔记（我的话+引用论文） | idea 看板 |
| ④ 装配 | `design/` | 设计草稿 + provenance 链 | C4 脊柱 |
| ⑤ 精炼 | `decisions/` | 决策工作表 → ADR | 选项×驱动力矩阵 |

均在 `docs/research-loom/` 下。源子目录按类型自动归类，开放集。

- **三种卡分家**：文献笔记（论文说）≠ 永久笔记（我说）≠ 设计（组装）。
- **provenance 链**：`design 的框 → ideas → 源卡`，任何设计选择可追回论文。
- **④↔⑤ 是循环不是单向**：看图→争议点决策→改图→再看。⑤ 是回灌 ④ 的精炼引擎。
- **append-only**：ADR 只增不删，旧决策标 `superseded-by`。

## 决定（已拍板）

- **D1 = 全搬（B-lite 执行）**：`git mv docs/research_results docs/research-loom` 整体搬入单一子文件夹，**保留 `papers/github/blogs/synthesis` 类型结构**（→ 内部 67 条卡间链接零破坏、git 历史保留），再加 `ideas/design/decisions/` 三个新阶段目录。仅修 3 处外部引用（`docs/index.md`、`CLAUDE.md`、`explain-paper` skill）。
- **D2**：`research-loom/design/` = 将来唯一设计家；`docs/design/` 暂冻结为 legacy，过渡期以前者为准。
- **载体**：纯 repo Markdown，Obsidian-ready。**卡间用相对 Markdown 链接**（可校验、可反链）；`[[ ]]` 不作链接机制（与散文示意冲突）。frontmatter 装结构化字段、视图与原子分家。

## 单元（每单元：docs 先行 → 测试 → 代码）

### U1 — 方法设计文档（docs 先行）
- 在 `docs/design/` 新增方法文档（中文）：五阶段不变量、三种卡的 frontmatter 契约、provenance 链规则、`4-design`↔`docs/design` 过渡关系。
- 更新 `docs/design/index.md`。
- 无代码，无测试（纯意图）。

### U2 — 内容区迁移（D1）✅
- **测试先行** `tools/check_doc_links.py`（独立可运行，跟随仓库 `experiments/` 脚本约定，无 pytest）：
  - 扫全仓相对 `.md` 链接，断言每个目标存在；danglers 则 exit 1。
  - 对抗自检 `--selftest`：外链跳过、锚点剥离、backtick/`[[ ]]` 非链接。
- **代码**：`git mv research_results→research-loom` + 加 `ideas/design/decisions/` + 各 index 重写 + 3 处外部引用修正 + `explain-paper` patch（本地，git-ignored）。
- **结果**：迁移零新增悬空；仅剩 3 条既有 `DEFINITION.md` 悬空（非本任务，记入 `docs/TODO.md`）。

### U3 — 模板（templates）
- **测试先行**：独立校验脚本核验五种模板 frontmatter 合规（必填字段、`status` 枚举、相对链接占位）。
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
