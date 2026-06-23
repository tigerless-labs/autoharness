---
id: ADR-0001
type: adr
status: proposed
affects: [G]
supersedes:
---
# 编辑把关采用结构门 + 人工复核可疑合并

> 走通样例，status proposed —— 由 [D-001](D-001-edit-gating.md) 坍缩的示范，待 user 接受/否决。**只增不删**：改主意写新 ADR 标 `supersedes`。

## 背景

held-out 门（[SkillOpt](../sources/papers/skillopt.md)）需 benchmark、环境门（[AutoHarness](../sources/papers/autoharness-lou.md)）需可判定合法性，本项目两者皆无，威胁"无需 oracle"这一驱动力。

## 决定

选 C：纯结构门为主、可疑合并提人工复核——兼顾"无需 oracle"与"低误拒"。

## 后果

- 好：主动路径无 oracle 依赖；可计算可审计。
- 差：引入人工复核环路，需测其成本（→ 可能的后续 ADR）。

## 重开条件

若出现低成本的 benchmark-free 自动判别证据，可重开并考虑去掉人工复核。
