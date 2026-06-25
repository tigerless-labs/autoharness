---
id: adherence-driven-curate
type: idea
status: 候选
---
# 经验生命周期管理：Hermes 式时间状态机为骨架，遵守度定生死留后

> 以 [Hermes](../sources/github/nousresearch-hermes-agent.md) curator 已落地机制为骨架；[ECC](../sources/github/affaan-m-ecc.md)「按遵守度定生死」的理念**留后**。user 认可，status 候选，待复核。

**主张**：符号沉淀后进入一条**永不终止的生命周期**——上浮、下沉、退役。骨架先用能跑的**时间状态机**；**用遵守度定生死的那一层留后**（见下）。

## 骨架（确定）

机制与触发时机拆开——机制可借 Hermes，时机不可照搬：

- **机制**：确定性失活状态机 `active → stale → archived`，再被用到即 reactivate；**只归档、不删除**（可逆）；成员资格按 [provenance 划线](lifecycle-by-provenance.md)；重组（合并近义 / umbrella）作可选的更贵一档，**默认不开**。
- **反思时校验（consolidation）**：每次在 [episode 边界反思](episode-boundary-reflection.md) 时，把新候选与已有 skill 校验，据此**更新已有 / 新建 / 删除**（Hermes `skill_manage`：add/replace/remove）——符号增删改的主入口，与失活状态机正交（一个管「和已有比怎么并」，一个管「没人用就退」）。
- **触发**：不照搬 Hermes 的常驻 daemon（Claude Code 等是临时进程，会话间无常驻、墙钟 sweep 无执行者）。改为**失活走惰性判定**（在 `SessionStart` / 注入那刻按时间戳现算 stale / 退役）、**去重走准入事件驱动**（新符号入场才比）。

**两轴正交**：「存活」轴管「用得好不好、活多久」，与「准入」轴（结构化冲突 / 重复 / 包含，管能不能进）分开。本卡的「矛盾」专指**符号 vs 实际行为**（说一套做一套），不是符号之间的冲突。

## 留后（留窗口，现在不做）

**用遵守度定生死**——把存活依据从**纯时间**升级为**被遵守 / 被矛盾**（被矛盾→下沉、被遵守 / 复现→上浮、跨项目复现→升 global、跌破阈值→事实性退役）。现在不做，因为：① 依赖已留后的使用日志 + 遵守度监控（见 [record-scenarios-for-eval](record-scenarios-for-eval.md)）；② ECC 设计了却从未实现，autoharness 也不一定好做。[dynamic-validation-lifecycle](dynamic-validation-lifecycle.md) 视它为**最终核心**，本卡 v1 先搁置。

## 论据 / 出处

- **骨架**来自 [Hermes](../sources/github/nousresearch-hermes-agent.md) curator（读源码核实）：确定性 `active→stale→archived`、never-delete-only-archive、pin 豁免、按记录 / 渠道圈范围、umbrella 合并默认关——目前唯一**实际在跑**的生命周期实现。
- **理念（留后）**来自 [ECC](../sources/github/affaan-m-ecc.md)：`observer.md` 写明遵守度标量动态，但代码审计证实**全是死规格**（无回读改写、活跃符号永不过期）——故是认可方向、未证可行。

## 待解 / 边界

- **失活刻度**：v1 用墙钟天；「使用相对」（几次会话未被用）更准，但需使用日志（已留后）。
- **会话边界覆盖盲区**：惰性 + `SessionStart` 触发意味着长期不开会话就不跑；是否需下次开会话补算积压、补算会否一次退役过多，待定。

## 关联

成员资格见 [按 provenance 划生命周期](lifecycle-by-provenance.md)；留后的遵守度轴接 [dynamic-validation-lifecycle](dynamic-validation-lifecycle.md)，其信号供料需 [从对话回合捕获](trace-based-pattern-extraction.md) / 使用日志（[record-scenarios-for-eval](record-scenarios-for-eval.md)，留后）。「退役 = 不再注入」依赖 [hook 强制注入](hook-forced-injection.md)。装配进 [design/](../design/index.md) 的 Manage 段。
