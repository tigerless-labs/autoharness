---
id: stage-skill
type: design
---
# 模块设计：stage_skill（reflector 的提案工具，emit-intent）

[reflector](reflector-subagent.md) 的**唯一写入面**——一个 **subagent-scoped 的 MCP 工具**。但它**不写 skill 树、不碰 live、也不写 staging**：只把一次 skill 改动**结构化地发成 intent**、append 进 per-run intent 队列。成型 / 校验 / 落盘全在确定性 [promoter](validate-store.md)（admission 模型）。读用宿主内建 `Read` / `Grep`；改动只此一途、**去掉通用 Write/Edit**。

## 为什么是 tool，不是通用 Write/Edit

- **input schema 在源头约束结构**：`{action, name, level, body | delta, reason, evidence}` 的必填 / 类型 / enum 让模型**填不齐 / 填歪就调不了**——结构性返工从源头消失，而非事后被 linter 拒、整轮浪费。可在入参即跑 Hermes 校验（frontmatter / size）给**当场反馈**。
- **LED 字段入参即保证**：`reason / evidence` 是必填参 → intent 必带 LED，[promoter](validate-store.md) 的"LED 有没有"几乎不可能被违反。
- **更紧的 least-privilege**：没有通用 Write/Edit，改动**只能**走它；**它只 append intent 队列、不碰任何 skill 树** → 模型结构上 land 不了，path-guard 降为 backstop。

它是**提案**的护栏，**不是闸、也不是写**——闸与落盘是 promoter 的（模型碰不到）。**tool 前置「结构」，promoter 兜「成型 + 内容 + 安全 + 落盘」。**

## intent 带什么

intent = **修改内容 + 元数据**，随 action 变：

| action | 修改内容 | 元数据 |
|---|---|---|
| `create` | **完整 body** | `name`、`level`（必填）、`reason`、`evidence` |
| `update`（整篇覆盖） | **完整 body** | `name`、`reason`、`evidence` |
| `patch`（小改首选） | **delta**（`old_string→new_string`，不带全文） | `name`、`reason`、`evidence` |
| `delete` | 无 | `name`、`reason`、`evidence` |

- **patch 只带 delta**：一行小改不必搬全文，promoter 用 `live + delta` 重建（"读 live"落在 promoter 应用 delta 那一刻）。
- **create / overwrite 带全文**：无 base 可依。
- intent **自带 LED**（`reason / evidence`）→ append 语义（详见 [validate-store](validate-store.md) 的 LED 节）。

成型为「最终全文」、读 live、原子落盘——**全是 promoter 的事**、不在本工具。

## global vs project（层）

- **create**：`level: global|project` 是**入参**、**默认 project**；global 高门槛（promoter 的 repo-agnostic 闸 + prompt 强调）。
- **update / delete**：模型只给 `name`，**层由 promoter 按两层并集定位现有 skill 解析**（扩 Hermes `_find_skill` 到两层，**同名跨两层 → 报错消歧**）；tool 可在入参做一次存在性检查给当场反馈。

## 复用 Hermes（相对 `skill_manager_tool.py`）

- **复用校验函数**（`_validate_frontmatter` / `_validate_content_size` / `_validate_file_path`）：**入参即时反馈**用一份、promoter linter 防御纵深再用一份（tool 是模型面，确定性侧别全信它）。
- **复用 `_find_skill`**（扩两层）：promoter 解析 update / delete 的层用，tool 入参存在性检查也可用。
- **不复用写 / 应用 / 回滚**：`_atomic_write_text`、patch 应用、write-first 回滚、`created_by` ContextVar、`_pinned_guard`——这些是 **promoter / Commit / MNG** 的事。tool 本身**不落任何盘**（除 append intent 队列）。

## 边界（与 promoter 分工）

schema 只保证**结构**（字段齐 / 类型 / level 合法）。**内容 / 交叉引用 / 安全 / 成型 / 落盘**它表达不了——引用文件存在、引用 tool 存在、占位符、global repo-agnostic、`skills_guard`、patch 成型、原子 rename——**全在 [validate-store](validate-store.md) 的 promoter**。

## 待解 / 动手前实测

- **MCP 工具能否 scope 到单个 subagent**（只 reflector 可见、正常会话不可见）：实测确认。
- 入参校验失败时，模型在 subagent 会话内**当场改**的闭环是否顺（vs 整轮重来）：实测。
- intent 队列的格式 / 持久性（崩溃补处理 vs 丢这轮）：与 [validate-store](validate-store.md) 待解同。

provenance：骨架 [Hermes](../sources/github/nousresearch-hermes-agent.md)（`skill_manager_tool` 的校验 + `_find_skill`）；校验项接 #416；least-privilege / 只写自产 [additive-over-native-skill](../ideas/additive-over-native-skill.md)；层选择见 [ref](ref.md) 的「放哪层」，成型 / 内容 / 安全 / 落盘见 [validate-store](validate-store.md)。
