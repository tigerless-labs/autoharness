---
id: episode-boundary-reflection
type: idea
status: 候选
---
# 按轮次在 episode 边界自动反思、整段蒸馏 skill——优于 ECC 逐调用从 hook 抓执行碎片

**主张**:经验沉淀的**触发与粒度**,应以一个完整任务轨迹(episode)为单位、在自然边界(一轮任务收尾)上整段反思一次,而不是像 [ECC](../sources/github/affaan-m-ecc.md) 那样在每次 PreToolUse/PostToolUse 上抓单条 tool I/O 碎片、再让后台 observer 从一个滚动 tail 里凑模式。[Hermes](../sources/github/nousresearch-hermes-agent.md) 的 `_iters_since_skill` 计数器——累计 tool 迭代,默认满 10,在 turn 收尾触发后台 fork **replay 整条刚跑完的 transcript** 再 `skill_manage`——正是这种"整段、按边界"的反思,它在四点上优于 ECC 的逐调用抓流:

1. **反思单位 = 完整 episode,而非截断的滚动窗口。** Hermes 反思一段语义完整、以 turn 收尾为界的轨迹;ECC 的 observer 读 `tail -n 500`,边界随 500 行任意切开,且 audit 实证 >500 obs/run 即成盲区。
2. **语义完整 = 含用户意图与最终结果,而非只有 tool I/O。** Hermes replay 的 transcript 带着"为什么(用户请求)"和"结果(最终答案)";ECC 的 hook **刻意不抓 user prompt**,只能从 re-edit/revert **反推**"用户纠正"——这正是 [直接读用户输入与 agent 输出](read-prompt-not-just-trace.md) 指出的缺口,而整段 replay 天然补上。
3. **连贯且便宜 = 同上下文 replay、命中 warm prefix cache,而非另起一次冷调用。** Hermes 的 fork 在原 turn 的暖缓存上整段重放(同 model、字节级前缀对齐、5 分钟 TTL 内);ECC 是对截断 tail 的一次 Haiku gestalt,无算法、不可复现。
4. **触发信号 = 工作量构成的 episode 边界(10 迭代≈"一个复杂任务"),而非无差别逐调用 + 计数/冷却批处理(每 20 obs / 60s)。**

**与 ECC 路线不是二选一,而是分层。** ECC 的 hook 抓取作为**数据搬运**仍有独到处——host-agnostic、不需占有 agent loop、对未"收尾"的会话也 100% 捕获(见 [从 trace 提模式](trace-based-pattern-extraction.md))。本卡主张的是**反思的粒度与时机**,与"用什么管道搬数据"正交:理想落地是把 Hermes 的反思粒度嫁接到 ECC 的捕获管道上。

## 论据 / 出处

源自 [Hermes-Agent](../sources/github/nousresearch-hermes-agent.md) 的 nudge-计数器机制(本会话读源码核实:`_iters_since_skill` 在主对话循环累加、turn 收尾满阈值即 `_spawn_background_review` fork 重放 transcript);对照 [ECC](../sources/github/affaan-m-ecc.md) 的 PreTool/PostTool hook 抓取 + 滚动 tail observer(2026-06-24 全源审计)。两者同属 [从 trace 沉淀经验](../synthesis/trace-to-experience.md) 方向的采集/触发前端,却选了不同的**反思单位**——这就是本卡判优的轴。

## 待解 / 边界

- **autoharness 多半不占有 agent loop**(它塑造 artifact、host 施加),拿不到 Hermes 那种"在循环里维护计数器 + fork 重放"的位置。落地形态应是:**用 ECC 式 hook 捕获作传输,但按 session/turn 把碎片归并、在 episode 边界整段反思**,而非照搬计数器。
- "10 迭代"是 Hermes 的工作量代理,不必是最优边界;autoharness 的 episode 边界按什么定(turn 结束 / 任务完成信号 / token 预算),待证据。

## 关联

承接 [从 trace 沉淀经验](../synthesis/trace-to-experience.md);与 [从 trace 提模式(借 ECC 捕获前端)](trace-based-pattern-extraction.md)(管道,正交)、[直接读用户输入与 agent 输出](read-prompt-not-just-trace.md)(被整段 replay 天然满足)交叉牵制。将装配进 [design/](../design/index.md) 的 Intake 段。
