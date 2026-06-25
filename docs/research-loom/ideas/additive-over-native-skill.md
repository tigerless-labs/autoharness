---
id: additive-over-native-skill
type: idea
status: 候选
---
# 不影响原生 skill 本来的功能：增强纯叠加、对原生零侵入

> user 提出的产品边界，status 候选，待 user 升 `采纳` 或改 `否决`。

**主张**：autoharness 对宿主的一切增强（hook 观察 / 强制注入 / 独立存储）必须是**纯叠加**，**不改变原生 skill 本来的功能与使用体验**——skill 的新增、读取、description 概率触发等既有路径维持原样，不被替换、拦截、降级。「走 hook 强制注入」是在原生之外**另开一条确定性通道**，而非接管或绕改 skill 加载本身；两条通道并存，用户对原有流程的感知不变。

**这条边界只管「不破坏原生固有功能」，与「维护」分开**：去重 / 退役 / 纠偏是生命周期组件（[滚动 curate](adherence-driven-curate.md)）的职责，不在本卡。本卡是一条**非功能约束**——我们的叠加零侵入原生；至于要不要回头维护原生 skill，是 [按 provenance 划生命周期成员](lifecycle-by-provenance.md) 的显式授权路径另说。它也是 [hook 强制注入](hook-forced-injection.md) 能被采纳的**前提**：可靠性的提升不得以牺牲原生功能 / 体验为代价。

## 论据 / 出处

[ECC](../sources/github/affaan-m-ecc.md) 的增强全程经由 SessionStart / UserPromptSubmit 等 hook 与独立的 instinct 存储实现，从不 patch 宿主内部、不改其 skill 加载器——即「在原生之外叠加」在工程上现成可行的实证。据此，叠加只在「原生留白处」加通道（hook 注入、独立存储），绝不重写原生 skill 的注册与读取链路。

## 关联

是 [hook 强制注入](hook-forced-injection.md) 的采纳前提（非功能约束）；与 [按 provenance 划生命周期成员](lifecycle-by-provenance.md) 划清边界——本卡管「默认不碰原生功能」，那条管「opt-in 维护原生 skill 时怎么安全地碰」（显式授权 + 可回滚 + 验证窗口）。
