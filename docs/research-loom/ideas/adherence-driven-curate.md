---
id: adherence-driven-curate
type: idea
status: 候选
---
# 经验生命周期管理:Hermes curator 式状态机为骨架,保留 ECC 的遵守度理念

> 以 [Hermes](../sources/github/nousresearch-hermes-agent.md) curator 的**已落地**机制为主,叠加 [ECC](../sources/github/affaan-m-ecc.md)「按遵守度定生死」的**理念**(它没实现、也不一定好实现)。user 认可,status 候选,待复核。

**主张**:符号沉淀后不是一次性打分,而是进入一条**永不终止的生命周期**——会上浮、下沉、退役。怎么实现分两层,**骨架先用能跑的,理念留作升级轴**:

**① 骨架(主,照 Hermes curator——已验证可落地)。** 必须把**机制**和**触发时机**拆开:机制可借,时机不可照搬。
- **机制(借 Hermes):** 确定性失活状态机 `active → stale(久未用) → archived(更久未用)`,再被用到就 reactivate;**只归档、不删除**(可恢复),退役可逆;成员资格按 [provenance 划线](lifecycle-by-provenance.md);重组(合并近义/umbrella)作为**可选**的、更贵的一档,默认不开。
- **触发时机(不照搬 Hermes 的 daemon):** Hermes 靠"空闲 2h、间隔 7d 自动醒"的**常驻 daemon**——但 Claude Code 等是**临时进程**,会话间无常驻、不会"空闲自动醒",墙钟周期 sweep **没有执行者**。改为:**失活走惰性判定**(墙钟天数只当判定谓词,在 `SessionStart`/注入符号那一刻用时间戳**现算** stale/退役,不靠 daemon fire),**去重走准入事件驱动**(新符号入场才比,本就不需 daemon)。

**② 理念(保留,照 ECC——方向认可但难实现):** 把"定生死"的依据从**纯时间(多久没用)**升级为**遵守度(被遵守 / 被矛盾)**。
- 被矛盾 / 被无视 → 下沉;复现 / 被遵守 → 上浮;跨项目复现 → scope 升 global;跌破阈值 → 事实性退役。
- **诚实**:这要可靠地测"符号 vs 实际行为是否一致",ECC 设计了却从未实现,**autoharness 也不一定好做**;所以它是骨架之上的**升级方向**,不是第一版前提。先有 Hermes 式时间/使用状态机能跑,再朝遵守度加权演进。

关键约束:这里的「矛盾」是**符号 vs 实际行为**(说一套做一套),**不是符号之间的矛盾**。后者(结构化冲突/重复/包含)属另一条**准入轴**,本卡只管「用得好不好」的存活轴。两轴正交:准入管**能不能进**,生命周期管**进来后活多久**。

## 论据 / 出处

**骨架来自 [Hermes](../sources/github/nousresearch-hermes-agent.md) curator(本会话读源码核实):** 确定性失活状态机 `active→stale(30d)→archived(90d)`、**never delete only archive**、pin 豁免、按记录/渠道圈定管理范围、LLM 合并(umbrella)`DEFAULT_CONSOLIDATE=False` 默认关。这是目前唯一**实际在跑**的经验生命周期实现——可直接当骨架借。

**理念来自 [ECC](../sources/github/affaan-m-ecc.md)(设计了没做):** `agents/observer.md` 写明标量动态(`+0.05`/确认、`-0.1`/矛盾、`-0.02`/周衰减、2+ 项目 avg≥0.8 升 global),但代码审计证实**全是死规格**——无代码回读改写 confidence,活跃符号永不过期。所以"按遵守度定生死"是**认可的方向、未证可行的实现**(也正是 [ECC 卡](../sources/github/affaan-m-ecc.md) 第 4 条 wedge)。两边互补:**Hermes 给可跑的退役骨架,ECC 给更优的决策信号——前者先落地,后者作演进。**

## 待解 / 边界

- **失活刻度:墙钟天 vs 使用相对。** 非 24h 激活时,"30 天没碰"语义可疑——日历 30 天里只开过两次会话,跟高频使用下 30 天没碰,完全不同。也许刻度该是**使用相对的**(几次会话 / 几次注入未被用)而非日历天;这又正好接回 ② 的遵守度/使用信号轴。
- **会话边界触发的覆盖盲区。** 惰性 + `SessionStart` 触发意味着**长期不开会话就不跑**;是否需要兜底(下次开会话时一次性补算积压),以及补算会不会一次退役过多,待定。

## 关联

成员资格规则见 [按 provenance 划生命周期](lifecycle-by-provenance.md)。与准入轴正交互补(准入 vs 存活)。「遵守度」信号若要实现,需 [直接读用户输入与 agent 输出](read-prompt-not-just-trace.md) / [历史 trace 提模式](trace-based-pattern-extraction.md) 供料。「退役 = 不再注入」依赖 [hook 强制注入](hook-forced-injection.md) 的注入闸。装配进 [design/](../design/index.md) 的 Manage 段。
