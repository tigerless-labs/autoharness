---
id: structural-gate-no-oracle
type: idea
status: 候选
---
# 用结构性检查给编辑把关，不要 held-out 分数

> 走通样例，status 候选，待 user 把它升 `采纳` 或改 `否决`。

**主张**：在主动路径上，仅凭技能文本的结构性操作（去重、冲突、边界）给编辑把关，不引入结果信号/oracle。把"是否接受一次编辑"从依赖评分的判断，变成可计算的结构判断。

## 论据 / 出处

[SkillOpt](../sources/papers/skillopt.md) 的 held-out 门需 benchmark，[AutoHarness (Lou)](../sources/papers/autoharness-lou.md) 的环境门需可判定合法性。本项目两者皆无，故转向结构——是 [离线评测验证](../synthesis/offline-validation.md) 的轻量替代（它跑实验验证，本卡只看结构）。

## 关联

待装配进 harness 编辑把关设计（草稿 v1 已删，待重做）；其落地选择见决策 [D-001](../decisions/D-001-edit-gating.md)。
