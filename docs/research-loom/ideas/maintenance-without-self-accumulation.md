---
id: maintenance-without-self-accumulation
type: idea
status: 候选
---
# 维护可脱离自积累单独成立——为「不想自动生成新 skill、但想自动维护已有 skill」的用户提供方案

> user 提出：这套生命周期也能服务只想维护、不想自积累的用户。status 候选，待复核。

**主张**：经验生命周期 / curate 机制对符号的**来源不可知**——它管机器自学出的符号，同样管用户手写的原生 skill。于是「**自积累**（自动生成新符号）」与「**维护**（对已有符号去重 / 退役 / 纠偏 / 上浮）」是**可解耦的两件事**，能分别交付。存在一类用户：不信任或不想要自动生成，却确实苦于手写 skill 越攒越多、互相打架、过期失效——给他们「**只维护、不生成**」的模式，是更低门槛的入口，也扩大可服务人群。

## 论据 / 出处

- [滚动 curate](adherence-driven-curate.md) 借的 [Hermes](../sources/github/nousresearch-hermes-agent.md) curator 骨架（失活状态机、never-delete-only-archive、按 provenance 圈管理范围）作用于「一个符号集合」，**不要求集合里的符号是机器生成的**——这正是「只维护」模式可独立成立的机制依据。
- 是 [按 provenance 划生命周期](lifecycle-by-provenance.md) 的**正向用例**：那条卡主张「默认只有机器自学经验进生命周期，其他来源 opt-in」；本卡即用户把**手写 skill opt-in 进维护、却不开自积累**——同一个 provenance 旋钮的两档。
- [skill 召回随数量恶化](skill-recall-low-degrades-with-n.md) 对手写 skill 同样成立，所以「自动维护已有 skill」有**独立刚需**，不依赖自积累。
- 定位含义：「只维护」对商业/谨慎用户尤其友好（无新增行为 = 低风险、易合规），是 audit/gate/rollback 治理卖点的**轻量入口**——呼应 general 滩头 vs 商业市场的排序。

## 待解 / 边界

- 与 [维护层只能叠加](additive-over-native-skill.md) 的张力：维护已有 skill 必然要改写/退役原生 skill，与「纯叠加、零侵入」边界直接冲突。只维护模式下「侵入」是**用户显式授权**的，需要一份不同于自积累模式的**授权 / 回滚契约**。
- 成品边界：「只维护」与「维护 + 自积累」是两个 SKU 还是一个开关，待定。

## 关联

是 [按 provenance 划生命周期](lifecycle-by-provenance.md) 的正向用例；复用 [滚动 curate](adherence-driven-curate.md) 的 curator 骨架；与 [维护层只能叠加](additive-over-native-skill.md) 张力待解。将装配进 [design/](../design/index.md) 的 Manage 段（兼产品定位）。
