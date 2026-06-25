---
id: record-scenarios-for-eval
type: idea
status: 候选
---
# 创建/更新/使用场景随符号留痕——为高频符号日后自举 per-symbol eval 预存素材（现阶段只记录、不验证）

> user 提出：造 skill 时连同凭据一起记下来，日后可成 eval 集。status 候选，待复核。

**主张**：符号（skill / 经验）在三个时刻都把**场景证据**作为随附数据持续记录——① **创建**时记下触发它的那组重复场景（凭什么造它）；② **每次更新**时记下本次改动的证据与场景（凭什么改）；③ **运行**时记下实际命中的使用场景（被召回时真实长什么样）。这些留痕本身**不裁决、不验证**，只是日后给**高频符号自举 per-symbol eval 集**的料。本卡范围严格限定在**捕获/记录**；replay/打分留到证据足够再开，是一道刻意的延迟。

## 论据 / 出处

- [SkillHone](../sources/papers/skillhone.md) 是直接范式：它把 skill revision 与 evaluation-side evidence 耦合，持久记录 diagnoses / revisions / evidence / outcomes，并论证「只留最终 artifact、丢掉决策史」是硬伤。本卡把这种「更新留痕」从它的专门机制，降为**每次 create/update/use 都顺手攒的常规副产物**——含被否决的备选，正是 autoharness 回滚故事要的审计轨。
- 下游对接 [离线评测验证](../synthesis/offline-validation.md) 的子类②（自有 trace 自举 eval）：本卡是其**上游备料**——把「日后要当验证集的料」在当场就攒好；并须守住该方向红线「生成某候选的 trace 不得验证它」，故创建/更新所凭场景与日后验证集**必须分账**。
- 创建所凭的「重复场景」即 [从 trace 提模式](trace-based-pattern-extraction.md) 的 3+ 复现，天然是该符号的**正例种子**；每次留痕发生在 [episode 边界](episode-boundary-reflection.md) 上，场景证据 = 该 episode 的 replay 切片。
- **不引入裁决，只预存素材**：本卡不下任何准入/验证判定，只把日后可能要的料先攒着——把「要不要自举 oracle」那道悬置问题，从「现在裁决」降级为「先把料攒着」。

## 待解 / 边界

- **脱敏前置**：使用场景含用户原话，PII/密钥风险高于 tool I/O（见 [直接读 prompt](read-prompt-not-just-trace.md)）——留痕入库前必须过红线过滤（CLAUDE.md 安全条款）。
- **配额与去重**：高频符号会堆大量使用场景，需采样/配额，免得留痕本身膨胀；每条须标 provenance（哪个 session/episode）以便日后 split。
- **何时从「只记录」转「开始验证」**：触发阈值（符号频次 / 场景累积量）待定，不在本卡内定。

## 关联

上游承 [从 trace 提模式](trace-based-pattern-extraction.md)、[episode 边界反思](episode-boundary-reflection.md)；下游喂 [离线评测验证](../synthesis/offline-validation.md) 子类②；成员资格随 [按 provenance 划生命周期](lifecycle-by-provenance.md)；使用场景同时供 [滚动 curate](adherence-driven-curate.md) 的「被遵守/被矛盾」判定。只存料、不裁决。将装配进 [design/](../design/index.md) 的 Intake/Manage 段。
