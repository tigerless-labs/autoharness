---
id: adherence-driven-curate
type: idea
status: 候选
---
# 滚动 curate：用「被遵守 / 被矛盾」的统计动态给符号定生死

> 借鉴 [ECC](../sources/github/affaan-m-ecc.md) 设计（它没实现），user 认可此方向，status 候选，待复核。

**主张**：符号的进化不是一次性打分，而是**永不终止的滚动 curate**——每个符号的权重随它在真实运行中**被遵守还是被违背**持续浮动：

- 被矛盾 / 被无视 → 权重衰减；
- 复现 / 被遵守 → 权重上升；
- 跨项目复现 → scope 由 project 升 global；
- 跌破阈值 → **事实性死亡**（不再注入，等于退役）。

关键约束:这里的「矛盾」是**符号 vs 实际行为**(说一套做一套),**不是符号之间的矛盾**。后者(结构化冲突/重复/包含)属另一条轴,归 [结构化把关](structural-gate-no-oracle.md);本卡只管「用得好不好」的使用信号轴。两轴正交:结构门管**能不能进**,滚动 curate 管**进来后活多久**。

## 论据 / 出处

[ECC](../sources/github/affaan-m-ecc.md) 的 `agents/observer.md` 写明了这套标量动态(`+0.05`/确认、`-0.1`/矛盾、`-0.02`/周衰减、2+ 项目且 avg≥0.8 升 global),但代码级审计证实**全是死规格**:无任何代码回读改写 confidence,confidence 写死一次,活跃符号永不过期。所以这是 ECC「设计了没做」的一块——思路成立,实现是 autoharness 的空白(也正是 [ECC 卡](../sources/github/affaan-m-ecc.md) 列出的第 4 条 wedge:真正不回退的滚动 curate)。

ECC 用标量打分当它**唯一的**「冲突」处理——没有结构化冲突扫描。我们认可标量动态作为**使用信号轴**,但不让它替代结构轴:autoharness 两者都要。

## 关联

与 [结构化把关](structural-gate-no-oracle.md) 正交互补(准入 vs 存活)。所需的「被遵守/被矛盾」信号,来自 [历史 trace 提模式](trace-based-pattern-extraction.md) 同一条抓取流。「事实性死亡 = 不再注入」依赖 [hook 强制注入](hook-forced-injection.md) 的注入闸作为退役开关。
