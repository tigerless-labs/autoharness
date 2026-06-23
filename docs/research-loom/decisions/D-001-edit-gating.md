---
id: D-001-edit-gating
type: decision
status: open
affects: [G]
---
# 决策：结构门怎么给编辑把关

> 走通样例，status open —— 真实取舍待 user 拍板。坍缩样例见 [ADR-0001](ADR-0001-structural-gate.md)。

## 驱动力（加权质量属性）

- 无需 oracle: 0.4
- 误拒正当并行专才: 0.3
- 可计算/可审计: 0.3

## 选项（set-based）

- A 借 [SkillOpt](../sources/papers/skillopt.md) held-out 门
- B 纯结构门（去重/冲突/边界），见 [结构化把关](../ideas/structural-gate-no-oracle.md)
- C 结构门 + 人工复核可疑合并

## 权衡（选项 × 驱动力 + 证据）

| | 无需oracle | 误拒 | 可审计 | 证据 |
|---|---|---|---|---|
| A | ✗需benchmark | 低 | 高 | [SkillOpt](../sources/papers/skillopt.md) |
| B | ✓ | 中（文本相似度难辨克隆/专才） | 高 | [AutoHarness](../sources/papers/autoharness-lou.md) |
| C | ✓ | 低 | 高 | — |

敏感点：oracle 依赖对 A 致命。权衡点：自动化程度 ↔ 误拒。可逆性：单向门（活动层接入难退）→ 需证据。还缺：C 的人工复核成本实测。
