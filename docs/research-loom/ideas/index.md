# ideas — ③ 蒸馏（永久笔记）

我认可的思路与自己的新念头，每条一卡：**用自己的话、原子化、引用所凭的来源卡**。永久笔记不是论文摘要，是你的主张。方法由 `research-loom` skill 承载。

- 🧭 **[核心理念：在运行中积累并验证经验，而非定期收集 eval 跑进化](dynamic-validation-lifecycle.md)** — `候选`（理念卡：in-loop 验证、离线 eval 会过期、replay 降兜底；机制归 episode/adherence，待复核）
- [要可靠生效的规则，走 hook 强制注入](hook-forced-injection.md) — `候选`（源于 ECC 实测，待复核）
- [不影响原生 skill 本来的功能：增强纯叠加、对原生零侵入](additive-over-native-skill.md) — `候选`（user 提出的产品边界；重点从「维护层叠加」改为「不破坏原生固有功能」，与维护分开，待复核）
- [候选来料：从对话回合捕获，而非只从 tool 执行反推](trace-based-pattern-extraction.md) — `候选`（合并原 read-prompt；借 ECC 前端 + 抓取口上移，待复核）
- [按轮次在 episode 边界自动反思、整段蒸馏 skill——优于 ECC 逐调用从 hook 抓碎片](episode-boundary-reflection.md) — `候选`（user 认可：Hermes 整段 replay 反思优于 ECC hook 抓流，待复核）
- [经验生命周期管理：Hermes 时间状态机为骨架，遵守度定生死留后](adherence-driven-curate.md) — `候选`（骨架=惰性失活状态机 + 反思时 skill_manage 增删改；遵守度轴留窗口，待复核）
- [按 provenance 划生命周期成员；默认机器自产入池、其余 opt-in（含「只维护」模式）](lifecycle-by-provenance.md) — `候选`（合并原 maintenance-without-self-accumulation，待复核）
- [skill 召回率本就不高，且随 skill 数量增长而恶化](skill-recall-low-degrades-with-n.md) — `候选`（user 提出：读取率不高、越多越差，待复核）
- [符号随附记录：v1 只做决策账本，使用·监控·验证留后](record-scenarios-for-eval.md) — `候选`（账本=创建/更新/退役事件 + 出生证据；trace 读宿主 log；使用/监控/验证留窗口，待复核）
- [经验沉淀后存哪一层：倾向 B 新增为 skill（参考 Hermes）、独立 instinct 层作苗圃](precipitate-storage-layer.md) — `候选`（user 取向 B：skill 可传播；正式 ADR 待开）
