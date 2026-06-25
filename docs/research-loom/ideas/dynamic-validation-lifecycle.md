---
id: dynamic-validation-lifecycle
type: idea
status: 候选
---
# 核心理念：在动态工作中积累并验证经验，而非定期收集 eval 跑进化

> user 倡导为**核心理念**（thesis 级）。status 候选，待复核。

**主张**：经验的积累**与验证**都应在**真实工作流里就地、随交互发生**（in-the-loop），而不是「定期攒一个 eval 集 → 离线跑一轮进化/裁决」。理由是环境**随每次交互漂移**：基于历史 trace 建的 eval 会过期——昨天验证成立的依据，今天的环境已不复存在，历史依据失效。因此验证必须**随用随验**：一个符号靠「在后续真实交互中持续被遵守、奏效」挣得存活，而非靠一次离线 replay 拿到的快照分；且**历史依据本身随环境衰减、退役**，不是永久 golden。

## 三道闸的重新分工（本理念的落点）

把「接不接受 / 活不活」拆三道，**动态验证升为主裁决**：

- **准入（即时·便宜）**：结构性检查——去重 / 冲突 / 边界，放行候选。
- **存活（持续·主）**：**动态验证**——在真实交互里持续被遵守 / 奏效才活，被矛盾 / 失效则下沉退役。即把 [滚动 curate](adherence-driven-curate.md) 里 ECC 的「遵守度」理念从「升级轴」提为**核心机制**。
- **兜底（重·偶尔）**：[离线 replay](../synthesis/offline-validation.md) 降为**高风险、或结构 + 动态都拿不准时**才动用，不再是常规裁决轴。

## 论据 / 出处

环境漂移使历史 eval 失效，是 [离线 replay 子类②](../synthesis/offline-validation.md) 在自评偏差（[SkillLens](../sources/papers/skilllens.md) 把上限按在 ≈46.4%）之外的**第二重隐患**——本理念再加一条「靶子本身在移动」。动态验证的可行机制来自 [直接读 prompt / 输出](read-prompt-not-just-trace.md)：遵守度**字面可观测**，使「随用随验」不必重放即可拿信号。定位上，这把 autoharness 与 [SkillOpt](../sources/papers/skillopt.md) / offline-eval 那种「周期收集 eval → 进化」家族**划开**。

## 待解 / 边界

- **重开决策**：本理念把 [离线 replay](../synthesis/offline-validation.md) 从「autoharness 的裁决轴（落子类②）」降为兜底——直接重开那条已采纳方向，须开 [决策工作表](../decisions/index.md)（驱动力：环境漂移下的有效性 / 成本 / 自评偏差 / 安全兜底）。
- **信号强度**：遵守度是弱信号（「照做了」≠「做对了」），高风险动作仍可能需兜底 replay——主 / 兜底边界按风险分。
- 与 [record-scenarios-for-eval](record-scenarios-for-eval.md) 的衔接：记录的使用场景不再只是「将来 eval 集的料」，而是**随用随验 + 随环境过期**的滚动证据。

## 关联

重排 [离线评测验证](../synthesis/offline-validation.md) 的地位（裁决轴 → 兜底）；把 [滚动 curate](adherence-driven-curate.md) 的遵守度理念提为核心；与结构性准入组成三道闸；给 [record-scenarios-for-eval](record-scenarios-for-eval.md) 的记录赋予「滚动过期」语义。是 DEFINITION 级理念，装配进 [design/](../design/index.md) 脊柱与定位。
