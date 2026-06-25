---
id: record-scenarios-for-eval
type: idea
status: 候选
---
# 符号随附记录：v1 只做决策账本，使用·监控·验证留后

> user 逐步收口。status 候选，待复核。

**主张**：符号（skill / 经验）的生平**随符号就地记录**，既作审计与回滚轨，也作日后 eval 的料。但 **v1 只做决策账本**；一切要"判好坏"的环节（使用日志、遵守度监控、验证）一律留后。

## 决策账本（v1 唯一要做的）

每个符号一本 append-only 账本，**创建 / 更新 / 退役**都是其上一条事件，同一套要素：**发生时刻、事件类型、为什么（触发或诊断）、改动了什么、证据**。

- **证据两件套**：一份**脱敏蒸馏切片**（durable 但残）+ 一个**指向宿主 log 的指针**（全但易断）。
- **创建证据当场物化**：创建低频且必须 durable，故立即把切片脱敏落盘、不靠指针（宿主 log 会轮转）；并标「不可自验」——生成某符号的 trace 不得验证它自己。
- **v1 无裁决**：没有"判收不收"这一步，反思提出一条即记一条，故账本不含 gate / outcome 要素。

## 存储与来料（已定）

- **trace 不自存**：完整上下文读宿主 log（如 Claude logs）按引用；留存不归我们管，要紧的就立刻物化脱敏。
- **账本随符号、不进 skill 体**：放符号旁 sidecar（按符号 id），不混入被注入的 skill 正文（护召回）；可随 skill 打包传播。
- **SkillHone 只借结构、不涉场景**：借其「诊断→改动→证据→结果」决策史骨架；其证据系 eval probe（我们延后）、且**根本不记场景**——创建 / 调用场景是 autoharness 自有，源出 ECC 抓取 / [从对话回合捕获](trace-based-pattern-extraction.md) / [离线评测验证](../synthesis/offline-validation.md) 子类②。

## 留后（只留窗口，现在不做）

- **使用日志**：每次调用的场景 + 指针 + 遵守度代理。
- **遵守度监控 / 动态验证**：见 [dynamic-validation-lifecycle](dynamic-validation-lifecycle.md)。
- **验证（replay / 打分）**，及「只记录 → 开始验证」的触发阈值。
- **裁决要素（gate / outcome）**：将来若恢复准入再加。

## 论据 / 出处

- [SkillHone](../sources/papers/skillhone.md)：决策史骨架的范式（持久记 diagnoses / revisions / evidence / outcomes + rejected）；但其证据系 eval probe、且**不记场景**，故只借结构。
- [从 trace 提模式](trace-based-pattern-extraction.md)：创建所凭的「复现场景」即正例种子。
- 留后的使用 / 验证须守 [离线评测验证](../synthesis/offline-validation.md) 子类② 的红线：生成某候选的 trace 不得验证它。

## 关联

上游承 [从 trace 提模式](trace-based-pattern-extraction.md)、[episode 边界反思](episode-boundary-reflection.md)；成员资格随 [按 provenance 划生命周期](lifecycle-by-provenance.md)；留后部分接 [dynamic-validation-lifecycle](dynamic-validation-lifecycle.md) 与 [滚动 curate](adherence-driven-curate.md) 的遵守度判定。将装配进 [design/](../design/index.md) 的 Intake/Manage 段。
