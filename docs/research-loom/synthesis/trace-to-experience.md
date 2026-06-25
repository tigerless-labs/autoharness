---
id: trace-to-experience
type: direction
---
# 方向：从 trace 沉淀经验（intake / 入料口）

一次运行留下的 trace（工具 I/O、对话、运行轨迹）如何被蒸馏、固化成可复用的经验（instinct / skill / memory）？把"以运行痕迹为底料、自动长出符号"的来源卡聚到一起对比。这是 autoharness 的**入料口**轴，与下游的编辑把关（准入）、[离线评测验证](offline-validation.md)（裁决）正交：本方向只问**料从哪来、怎么沉淀**——trace 在此是**候选来料**（挖复现模式→候选符号，决定「提出什么」），而非[裁决轴](offline-validation.md)里把 trace 当**验证集/真值**（决定「接不接受」）。同一条 trace 不能既生成某候选又验证它（=训练集当测试集），故二者取的痕迹须物理隔离。

**硬边界（定义）**：本方向特指**不需要任何已标注 benchmark、只基于历史 trace 的经验沉淀**。料口是真实运行留下的痕迹（工具 I/O、用户对话、运行轨迹），靠频次 / 复现 / 召回 / 容量这类**无标注信号**沉淀——不预设带 ground-truth 标签的成功/失败轨迹，也不靠可判定 oracle 打分。凡是以"已标注 benchmark / 可判定 oracle"为前提才跑得动的蒸馏，不属于本方向。

## 概念矩阵：本方向（benchmark-free · 仅历史 trace）

| 来源 | 原料 | 蒸馏机制 | 沉淀产物 | 沉淀闸门 | 我的评判 |
|---|---|---|---|---|---|
| [ECC](../sources/github/affaan-m-ecc.md) | tool I/O（读不到 prompt，纠正靠反推） | 单次 Haiku 扫 500 行尾窗找 3+ 复现 | instinct（Action+Evidence + 频次 confidence） | 乐观写入、**无门**（curate 是死规格） | 采纳抓取+一次性生成前端；否决"沉淀无闸" |
| [Hermes-Agent](../sources/github/nousresearch-hermes-agent.md) | 复杂任务后的轨迹 | 任务后自主造 skill + 容量驱动 consolidation | skill（SKILL.md）+ MEMORY/USER 平文件 | 容量上限触发 add/replace/remove | 采纳：maintain-not-grow 的生产样例 |
| [OpenClaw](../sources/github/openclaw.md) | 短期会话信号 | 后台 Dreaming cron consolidation | MEMORY.md | **recall-utility** 门（score+召回频次+查询多样性） | 存疑：门是召回效用非净改善，off 验证谱系 |

## 界外对照（需 oracle/benchmark，或原料非 trace——剔除/保留作反证与祖型）

按硬边界，下列来源**不入本方向**：

- ~~Trace2Skill~~ — **已剔除**：须先 roll out 出**带标注的成功+失败轨迹**才能并行提 patch，前提就是一个已标注 benchmark，与"只基于历史 trace"直接冲突。
- [SKILL.md Mining](../sources/papers/skillmd-mining.md) — **否决其方法**，但保留为本方向最有力的**反证**：用 benchmark + 学到的 offline reward 去挖 trace，可读却不可迁移、丢序、还输给一个频次先验——正说明沉淀该走 benchmark-free 且 gate on 净改善。
- [Reflexion](../sources/papers/reflexion.md) — **祖型**：`经验→反思→符号` 的反向通路；机制本身与 benchmark 无关，但其 demo 依赖环境的成功/失败反馈，故列界外。
- [Socratic-SWE](../sources/papers/socratic-swe.md) — trace-bootstrapping 的正面样例，但筛选靠 **execution 验证 + solver-gradient 奖励**（可判定 oracle），不满足 benchmark-free；可借的只是"只留有用派生物"的选择思路。
- [OpenHuman](../sources/github/tinyhumansai-openhuman.md) — 无 benchmark，但**原料是外部集成数据、不是 trace**，在料口这一维就出界；保留以对照其记忆树结构（树 vs 我们的 DAG）。

## 小结

**共识**：历史 trace 是无标注、可规模化的经验底料——[Reflexion](../sources/papers/reflexion.md) 立下 `经验→反思→符号` 祖型，benchmark-free 系统（ECC/Hermes/OpenClaw）在生产里把它跑通。

**分歧**：沉淀闸门各不相同且大多不对齐"任务改善"——ECC 乐观无门、OpenClaw 召回效用、Hermes 容量上限。原料口也分裂：多数只抓 tool I/O，读不到用户原话。

**空白 / wedge**：在 benchmark-free 的硬约束下，几乎所有系统都把**沉淀**与**准入裁决**混为一谈或省掉了门，且都从 tool 执行反推意图。autoharness 的切口是把 trace 当**候选来料而非裁决**，并把抓取口从执行上移到对话回合。[SKILL.md Mining](../sources/papers/skillmd-mining.md) 的反证压住底线：沉淀产物必须 gate on **净改善**，不能 gate on 可读性、更不能靠 offline proxy reward。

**已蒸馏的 idea**：本方向直接喂养 [从历史 trace 提模式](../ideas/trace-based-pattern-extraction.md)（候选来料）、[直接读用户输入与 agent 输出](../ideas/read-prompt-not-just-trace.md)（上移抓取口）、[滚动 curate](../ideas/adherence-driven-curate.md)（沉淀后的存活信号）。
