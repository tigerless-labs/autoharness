---
id: additive-over-native-skill
type: idea
status: 候选
---
# 维护层只能叠加，不得改写原生：保住 Claude Code skill 模式的原生性

> user 提出的产品边界，status 候选，待 user 升 `采纳` 或改 `否决`。

**主张**：维护层对 Claude Code 的一切增强（hook 观察 / 强制注入 / 载体改写）必须是**纯叠加**，对原生 skill 机制与其使用体验**零侵入**——skill 的新增、读取、description 概率触发等既有路径维持原样，不被替换、不被拦截、不被降级。「走 hook 强制注入」是在原生之外**另开一条确定性通道**，而非接管或绕改 skill 加载本身；两条通道并存，用户对原有流程的感知不变。这条边界是 [hook 强制注入](hook-forced-injection.md) 能被采纳的**前提**：可靠性的提升不得以牺牲原生体验为代价。

## 论据 / 出处

[ECC](../sources/github/affaan-m-ecc.md) 的增强全程经由 `SessionStart` / `UserPromptSubmit` 等 hook 与独立的 instinct 存储实现，从不 patch Claude Code 内部、不改其 skill 加载器——即「在原生之外叠加」在工程上现成可行的实证。据此，维护层的载体选择只在「原生留白处」加通道（hook 注入、常驻上下文），绝不重写原生 skill 的注册与读取链路。

## 关联

是 [hook 强制注入](hook-forced-injection.md) 的采纳前提（非功能约束）。与 [结构化把关，不要 held-out 分数](structural-gate-no-oracle.md) 同属「维护层主张」。
