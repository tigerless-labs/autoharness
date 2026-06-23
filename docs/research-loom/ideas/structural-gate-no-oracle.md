---
id: structural-gate-no-oracle
type: idea
status: 候选
---
# 用结构性检查给编辑把关，不要 held-out 分数

> 走通样例，status 候选，待 user 把它升 `采纳` 或改 `否决`。

**主张**：在主动路径上，仅凭技能文本的结构性操作（去重、冲突、边界）给编辑把关，不引入结果信号/oracle。把"是否接受一次编辑"从依赖评分的判断，变成可计算的结构判断。

## 论据 / 出处

[SkillOpt](../papers/skillopt.md) 的 held-out 门需 benchmark，[AutoHarness (Lou)](../papers/autoharness-lou.md) 的环境门需可判定合法性——见方向 [edit-gating](../synthesis/edit-gating.md)。本项目两者皆无，故转向结构。与 [benchmark-free 验证谱系](../synthesis/benchmark-free-validation.md) 一致。

## 关联

装配进 [harness 编辑把关设计](../design/harness-edit-gate.md)；其落地选择见决策 [D-001](../decisions/D-001-edit-gating.md)。
