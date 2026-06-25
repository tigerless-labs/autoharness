---
id: precipitate-storage-layer
type: idea
status: 候选
---
# 经验自动沉淀后存在哪一层——倾向 B（新增为 skill，参考 Hermes），独立 instinct 层留作苗圃

> 原为开放问题。user 取向：**选 B，沉淀物长成原生 skill**（参考 [Hermes](../sources/github/nousresearch-hermes-agent.md)），新增驱动力 = **可传播**（skill 是天然可分发单元，独立 instinct 私有层不便传播）。status 升 候选；正式坍缩成 ADR 待开。

## 取向（user）

倾向 **B**：沉淀物固化为原生 skill，复用注册/读取链路，且**便于在用户间传播分享**。两条遗留张力转由别处消化，不在本卡内重证：

- 「B 是否仍算纯叠加」（[维护层只能叠加](additive-over-native-skill.md) 的边界）：维护已有 skill 必然要改写/退役，授权与回滚契约由 [维护脱离自积累](maintenance-without-self-accumulation.md) 处理。
- 「原生 skill 机制能否承载 curate 退役」：保留**混合解**作落地路径——沉淀先入独立 instinct 层做 curate（苗圃），存活到阈值再「毕业」固化为可分发 skill（成品架）。

**问题**（原始陈述，保留）：维护层把 trace 蒸馏出的经验固化为符号后，这些符号的**存储形态**该是什么？两条候选：

- **A — 独立一层（instinct-like）**：另开一类 rule.md / instinct 存储，与原生 skill 平级、彼此隔离；维护层全权管它的增删改与注入，不经过 skill 注册链路。
- **B — 新增为 skill**：沉淀产物直接长成原生 skill（SKILL.md），复用既有的注册、读取、description 概率触发路径，不另立存储。

两条的真正分歧在**「谁来管生死、走哪条召回通道」**：A 把沉淀物关进维护层私有、确定性注入的格子；B 把它交还原生机制、随概率触发浮沉。这不是命名之争——它决定了 curate、注入可靠度、与原生体验侵入度三者怎么摊。

## 论据 / 出处

来料同源、产物形态却分裂：[从 trace 沉淀经验](../synthesis/trace-to-experience.md) 的「沉淀产物」列已记下三系——[ECC](../sources/github/affaan-m-ecc.md) 落 **instinct**（独立存储，选 A）、[Hermes-Agent](../sources/github/nousresearch-hermes-agent.md) 任务后**自造 skill**（选 B）、[OpenClaw](../sources/github/openclaw.md) 落 **MEMORY.md**（第三形态）。生产系统并未对齐，说明这是真分歧而非已解问题。

两条候选各自被别的卡牵制，尚不能独立判定：

- 选 A 与 [hook 强制注入](hook-forced-injection.md) 天然契合——独立层正好挂确定性注入通道；且 [滚动 curate](adherence-driven-curate.md) 的「事实性死亡 = 不再注入」需要维护层能直接退役一个符号，独立层给得起这个开关，原生 skill 的注册链路则不一定。
- 选 B 复用原生触发，但 [维护层只能叠加，不得改写原生 skill 体验](additive-over-native-skill.md) 划下的边界要求零侵入——若沉淀物混进原生 skill 池并被维护层增删改，是否仍算「纯叠加」存疑。

注意与 [hook 强制注入](hook-forced-injection.md) 的分工：那条卡问的是**「一条规则按可靠度选哪个注入载体」**（hook / 常驻 / description-skill），是 forward path 的路由；本卡问的是**沉淀物本身存成什么、归哪一层、谁管它的生死**，是存储与治理。载体选择可以横跨任一存储形态，二者正交。

## 待解 / 什么证据会定生死

- 选 B 时，原生 skill 机制能否承载滚动 curate 的 confidence 衰减与「事实性死亡」？还是必须退回独立层才管得动退役？
- 选 A 时，独立层如何不重复 skill 的能力（bundle / 依赖 / 渐进披露），避免造第二套 skill 系统？需读 ECC instinct 存储与 Hermes skill 自造两端的实现再判。
- 是否存在**混合解**：沉淀先入独立 instinct 层做 curate，存活到阈值的再「毕业」固化为原生 skill——把 A 当苗圃、B 当成品架。

## 关联

直接源于 [从 trace 沉淀经验](../synthesis/trace-to-experience.md) 的「沉淀产物」分歧。与 [hook 强制注入](hook-forced-injection.md)（载体路由，正交）、[滚动 curate](adherence-driven-curate.md)（治理需求，约束选型）、[维护层只能叠加](additive-over-native-skill.md)（侵入度边界，约束选 B）三者交叉牵制。定生死前不装配进 [design/](../design/index.md)；坍缩时应开一张 [决策工作表](../decisions/index.md)（驱动力：curate 治理力 / 注入可靠度 / 原生零侵入 / 不造第二套 skill 系统）。
