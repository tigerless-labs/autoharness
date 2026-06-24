# Synthesis notes

Cross-source analysis that no single source owns. Per-source detail lives in the [papers/](../sources/papers/index.md), [github/](../sources/github/index.md), and [blogs/](../sources/blogs/index.md) cards; these notes only hold what emerges *across* them.

- [方向：离线评测验证 harness 更改](offline-validation.md) — `type: direction`：裁决轴；为验 update 离线跑实验，分①外部 benchmark ②自举 eval+replay 两子类；代价重。
- [方向：从 trace 沉淀经验](trace-to-experience.md) — `type: direction`：**benchmark-free、仅基于历史 trace** 的入料口对比（ECC/Hermes/OpenClaw 在内；需 oracle/benchmark 的方法列界外），闸门与原料口的分歧即 wedge。
- [方向：skill 的召回率与执行率](skill-recall-execution.md) — `type: direction`：注入/召回/执行三段拆分 + 各来源量到哪一段；直接量召回的同行评审≈空白，召回杠杆=描述卫生+结构去重。
