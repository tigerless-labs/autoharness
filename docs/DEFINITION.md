# autoharness — 项目定义

> 单一权威定义。设计细节见 [`design/`](design/index.md)。工作记录,不受设计文档风格规则约束。
> 记录:2026-06-23(本版取代旧的「结果驱动维护器」定义)。

## 1. 是什么

把 agent 的 **skill 层当一张 typed DAG 来管理**:从经验里**沉淀**新 skill,在图上理清**关系**、消解**冲突**与**冗余**、对**新增**把关,再做依赖感知**召回**。每个 skill 挂着「为何诞生、为何每次更新」的**理由账本**,作为未来进化的根基。

## 2. 解决的痛点

skill / 符号层只增不理 → **膨胀、冲突、冗余、召回不准、难维护**。

- 证据:ETH《Evaluating AGENTS.md》(context 文件可降成功率、涨成本);Anthropic「fewer, non-conflicting skills outperform sprawling libraries」;社区实践两月增 163%、被迫手动收敛 87→70。
- 空白:现有工作要么作用在**结构化 benchmark skill** 上(SkillDAG / Graph-of-Skills / SkillOps),要么是**固定规则的静态 linter**(AgentLint)。**没人在真实符号层做「关系 + 冲突 + 去重 + 召回」的结构化管理。**

## 3. 做它的逻辑

把扁平 skill 堆变成 **typed 关系图**,冲突 / 冗余 / 召回就从「靠判断」变成「靠结构」——**纯文本可算,无 oracle,绕开自评偏差**。沉淀 → 管理 → 召回,闭合一个**不依赖结果信号**的静态管理回路。结果信号(用量、成败)**预留在 eval 层**,作为日后进化的根基,先不进主回路。

## 哲学(北极星)

**符号学习的血脉。** 冻结的权重 + 一个外部可读、可改、可验、可删的符号结构;经验沉淀为**符号**,而不是梯度进权重。能力长在权重之外、且可持续维护——这是这条路的根。看过当前一批 skill 进化论文后,我们的修正如下。

**agent 是动态的。** 用固定的、或纯历史的 trace 当进化依据,容易**制造噪声**:昨天的状态未必是今天的标准,拿任一历史问题去验当前状态都不合理。**更好的进化触发点,是 agent 工作中当下遇到的新「好 / 不好」点**——信号新鲜、且省 token——把它留存下来。

**方向与刹车,合成闭环。** **新经验是进化方向**(向前的驱动);**旧的 eval 与历史决策是避免回退的参照**(向后的刹车,嫌重就只当参考、不强加)。一推一拉,闭合一个进化回路。

**无任何人为标注依赖。** 整条回路不靠人打标签。

> 现阶段先交付静态结构管理层(主回路);这套哲学经 [`design/eval.md`](design/eval.md) 的预留 eval 层落地——in-work 的好 / 坏点喂理由账本,新经验驱动进化,旧账本防回退。

## 4. 管线

```
经验 ─► 沉淀(新 skill) ─► 管理(typed DAG:关系 / 冲突 / 去重 / 新增把关) ─► 召回(依赖感知)
                                 每个 skill ⟂ 理由账本 ─► (预留)eval 层
```

四层见 [`design/workflow.md`](design/workflow.md);DAG 管理见 [`design/management.md`](design/management.md);预留 eval 见 [`design/eval.md`](design/eval.md)。

## 5. 借 / 造

| 能力 | 借 |
|---|---|
| 经验沉淀(observe → skill 增长引擎) | ECC |
| typed 图 + 冲突 / 重复边 + 召回 | SkillDAG |
| 预算内依赖感知召回 | Graph-of-Skills |
| 语义去重 | SkillReducer |
| skill 历史 / 决策账本(含被否选项,轻量 eval 参照) | SkillHone |

**造(无人覆盖):** 这套跑在**真实 prose 符号层**(而非结构化 benchmark skill)+ **per-skill 理由账本**(eval 根基)。

## 6. 范围

code agent,Claude Code 的 skill 层优先。
