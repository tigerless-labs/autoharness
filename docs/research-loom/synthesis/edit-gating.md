---
id: edit-gating
type: direction
---
# 方向：harness 编辑的把关（gate）

> research-loom 建立时的首个走通样例，判断列待 user 复核。

一次 harness/skill 编辑要不要接受，靠什么把关？把"带把关机制"的来源卡聚到一起对比。与 [benchmark-free 验证谱系](benchmark-free-validation.md) 紧邻。

## 概念矩阵（来源 × 维度 + 我的评判）

| 来源 | 把关机制 | 需要 oracle | 适用反馈 | 我的评判 |
|---|---|---|---|---|
| [SkillOpt](../papers/skillopt.md) | held-out 验证分数严格改善 | 需（benchmark） | 有评分的稠密反馈 | 存疑（与 benchmark-free 冲突） |
| [AutoHarness (Lou)](../papers/autoharness-lou.md) | 环境反馈迭代（非法动作清零） | 需（可判定合法性） | 规则清晰、即时反馈 | 存疑（TextArena 之外失效） |

## 小结

两者的把关都依赖本项目没有的东西（held-out 分数 / 可判定合法性）。**空白**：稀疏反馈、模糊合法性下如何给编辑把关——正是 autoharness 的 wedge。值得蒸馏成 [结构化把关](../ideas/structural-gate-no-oracle.md)。
