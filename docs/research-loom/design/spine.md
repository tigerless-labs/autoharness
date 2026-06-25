---
id: spine
type: design
---
# 系统架构：autoharness workflow v0

autoharness 在 agent 的真实运行中积累经验、并就地验证经验：经验不靠一次离线 eval 拿快照分，而是靠在后续交互里持续被遵守、奏效挣得存活，被矛盾 / 失效则退役。

实现上，它在宿主 agent 之外**纯叠加**地运行：经 hooks 观察会话，把 trace 里总结出的有效、可复用经验沉淀成符号（skill），按可靠度注回宿主，并管理这些符号的生命周期；对原生 skill 加载链路零侵入，增强只走 hooks 与独立存储。一条学习管道（CAP→REF→ADM→STO→INJ）把经验沉淀成符号、再注回宿主，一条生命周期分支（STO→MNG）决定符号活多久，闭成回路。

```
┌──────────────────────── 宿主 agent（host-agnostic）— autoharness 纯叠加、零侵入 ────────────────────────┐
│            会话运行   ·   原生 skill 加载（name+desc 进上下文 → description 概率触发）                  │
└───┬────────────────────────────────────────────────────────────────────────────────────▲────────────┘
    │ 观察 · hooks 抓对话回合                                                         注入 │
    ▼                                                                                      │
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│ CAP 捕获│──►│ REF 反思│──►│ ADM 准入│──►│ STO 存储│──►│ INJ 注入│──────────────────────┘
└────┬────┘   └─────────┘   └─────────┘   └────┬────┘   └─────────┘
     │ 原始 trace                              │
     ▼ 指针入宿主 log（入口脱敏）              ▼
  [宿主 log]                            ┌──────────────┐
                                        │ MNG 生命周期 │  失活状态机 active→stale→archived（惰性 · 按 provenance）
                                        └──────────────┘
                                        每符号随附 LED 账本（sidecar：创建 / 更新 / 退役 + 出生证据）
```

## 组件职责

- **CAP 捕获** — host-agnostic hook 抓每个对话回合（用户输入 + agent 输出 + tool I/O），只搬运不裁决；入口过脱敏红线；原始 trace 不自存，按指针引宿主 log。
- **REF 反思** — 在 episode 边界对整段 transcript replay 一次、整段蒸馏候选符号，以完整任务为单位，而非逐调用抓碎片。
- **ADM 准入** — 即时便宜的结构闸：去重 / 冲突 / 边界 / 描述卫生，放行候选；不依赖 oracle 或 benchmark。
- **STO 存储** — 候选固化的落点：原生 skill（可传播）+ instinct 苗圃。存储形态未定。
- **INJ 注入** — forward path 的载体选择：must-always 规则走 hook 强制注入（确定性），其余交回原生 description（概率触发）。
- **MNG 生命周期** — 确定性失活状态机 active→stale→archived，惰性判定（SessionStart 现算）、只归档不删除、按 provenance 圈成员。
- **LED 账本** — 每符号 sidecar 的 append-only 决策账本（创建 / 更新 / 退役 + 出生证据），不进 skill 体以护召回。

## 决策

- **纯叠加、零侵入原生**：增强全程经 hooks + 独立存储，不改宿主 skill 注册 / 读取链路；可靠性提升不以牺牲原生体验为代价。
- **trace 当候选来料、不当裁决**：抓取口从工具执行上移到对话回合；同一条 trace 不得既生成又验证某符号（生成≠验证隔离）。
- **must-always 走确定性载体**：必须每次生效的规则不靠概率召回，做成 hook 强制注入。
- **退役即不再注入、只归档不删除**：默认动作保守（失活 / 可逆归档），改写 / 合并须显式 opt-in；默认只有机器自产符号进生命周期。

## 待解

- **STO 沉淀存哪层**（原生 skill / instinct 苗圃 / 混合）——待开 [decisions/](../decisions/index.md)。
- **动态验证**：符号靠遵守度随用随验挣存活，留后；当前 MNG 先用时间刻度兜底。
- **兜底重放**：离线 replay 仅高风险时动用，地位待决策。
- **episode 边界信号**（turn 结束 / 任务完成 / token 预算）未定。

---

provenance（idea ↔ 元素是**多对多**，非一一对应——理念 / 约束类 idea 跨多个元素，单个元素也可叠合多张；下面只标主要所凭）：

- **横切（跨多元素 / 理念 / 约束）**：[dynamic-validation-lifecycle](../ideas/dynamic-validation-lifecycle.md)（理念，贯穿全管道）、[additive-over-native-skill](../ideas/additive-over-native-skill.md)（零侵入，约束 STO/INJ/MNG）、[skill-recall-low-degrades-with-n](../ideas/skill-recall-low-degrades-with-n.md)（召回，驱动 ADM 准入闸 + MNG 删冗余）、[lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)（成员资格，约束 MNG 谁进 + STO 可传播）、[record-scenarios-for-eval](../ideas/record-scenarios-for-eval.md)（账本 LED，随附所有元素的事件）。
- **各元素主要所凭**：CAP←[trace-based-pattern-extraction](../ideas/trace-based-pattern-extraction.md)（含读 prompt/输出）；REF←[episode-boundary-reflection](../ideas/episode-boundary-reflection.md)；ADM←skill-recall（见上）；STO←[precipitate-storage-layer](../ideas/precipitate-storage-layer.md)；INJ←[hook-forced-injection](../ideas/hook-forced-injection.md)；MNG←[adherence-driven-curate](../ideas/adherence-driven-curate.md)。

设计元素是 idea 的**装配**，不是 idea 的容器：元素按管道职责切分，与 idea 卡不一一对应。每个元素的设计细节落在其**单独的模块设计文档**（per-module，待补）；idea 只是上游素材，不等于设计。
