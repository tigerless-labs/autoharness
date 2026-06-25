---
id: dynamic-validation-lifecycle
type: idea
status: 候选
---
# 核心理念：在运行中积累并验证经验，而非定期收集 eval 跑进化

> user 倡导为核心理念（thesis 级）。status 候选，待复核。

**主张**：经验的积累**与验证**都应在**真实工作流里就地、随交互发生**（in-the-loop），而非「定期攒一个 eval 集 → 离线跑一轮进化 / 裁决」。理由是环境**随每次交互漂移**：基于历史 trace 建的 eval 会过期——昨天验证成立的依据，今天的环境已不复存在。所以验证不是一次离线 replay 拿到的快照分，而是随后续真实运行**就地累积**；历史依据本身随环境衰减、退役，不是永久 golden。

## 落点：验证内生于沉淀回路，不另起裁决子系统

本理念**不**新增一套独立验证机制，而是让验证落在已有回路上：

- **就地验证（现行）**：每次在 episode 边界反思时，把新蒸馏的候选与**已有 skill 校验**，据此**更新 / 新建 / 删除**（[episode 边界反思](episode-boundary-reflection.md) 的 Hermes consolidation）；加上 [滚动 curate](adherence-driven-curate.md) 的确定性失活状态机（长期不被用 → stale → 退役）。机制与时机归这两张卡，本卡只立理念。
- **遵守度动态验证（留后）**：把存活依据从「时间 / 使用」升级为「被遵守 / 被矛盾」（说一套做一套即一次矛盾），是更强的随用随验；但依赖留后的使用日志 + 遵守度监控，[滚动 curate](adherence-driven-curate.md) 已将其标为留后。
- **离线 replay（兜底）**：[离线评测验证](../synthesis/offline-validation.md) 从裁决轴降为**高风险时才动用**的兜底，不再是常规轴。

## 论据 / 出处

环境漂移使历史 eval 失效，是 [离线 replay 子类②](../synthesis/offline-validation.md) 在自评偏差（[SkillLens](../sources/papers/skilllens.md) 把上限按在 ≈46.4%）之外的**第二重隐患**——靶子本身在移动。定位上，这把 autoharness 与 [SkillOpt](../sources/papers/skillopt.md) / offline-eval 那种「周期收集 eval → 进化」家族**划开**。

## 待解 / 边界

- **重开决策**：把 [离线 replay](../synthesis/offline-validation.md) 从已采纳的「裁决轴」降为兜底，须开 [决策工作表](../decisions/index.md)（驱动力：环境漂移下的有效性 / 成本 / 自评偏差 / 安全兜底）。
- **信号强度**：时间 / 使用是弱存活信号；遵守度（留后）更强但「照做了」≠「做对了」，高风险动作仍可能需兜底 replay。

## 关联

机制归 [episode 边界反思](episode-boundary-reflection.md)（反思时校验 → 更新 / 新建 / 删除）与 [滚动 curate](adherence-driven-curate.md)（失活状态机 + 遵守度留后）；重排 [离线评测验证](../synthesis/offline-validation.md) 的地位（裁决轴 → 兜底）；给 [record-scenarios-for-eval](record-scenarios-for-eval.md) 的记录赋予「滚动过期」语义。是 DEFINITION 级理念，装配进 [design/](../design/index.md) 脊柱与定位。
