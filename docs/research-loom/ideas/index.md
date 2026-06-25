# ideas — ③ 蒸馏（永久笔记）

我认可的思路与自己的新念头，每条一卡：**用自己的话、原子化、引用所凭的来源卡**。永久笔记不是论文摘要，是你的主张。方法见 [`../../design/research-loom.md`](../../design/research-loom.md)。

- 🧭 **[核心理念：在动态工作中积累并验证经验，而非定期收集 eval 跑进化](dynamic-validation-lifecycle.md)** — `候选`（user 倡导为核心理念；把离线 replay 从裁决轴降为兜底，重开决策，待复核）
- [要可靠生效的规则，走 hook 强制注入](hook-forced-injection.md) — `候选`（源于 ECC 实测，待复核）
- [维护层只能叠加，不得改写原生 skill 体验](additive-over-native-skill.md) — `候选`（user 提出的产品边界，待复核）
- [从历史 trace 里提模式：候选符号的无标注来源](trace-based-pattern-extraction.md) — `候选`（借鉴 ECC 抓取前端，待复核）
- [按轮次在 episode 边界自动反思、整段蒸馏 skill——优于 ECC 逐调用从 hook 抓碎片](episode-boundary-reflection.md) — `候选`（user 认可：Hermes 整段 replay 反思优于 ECC hook 抓流，待复核）
- [经验生命周期管理：Hermes curator 状态机为骨架，保留 ECC 遵守度理念](adherence-driven-curate.md) — `候选`（以 Hermes 已落地机制为主 + ECC 遵守度理念为升级轴，待复核）
- [默认只有机器自学经验进生命周期；其他来源可 opt-in 自动沉降](lifecycle-by-provenance.md) — `候选`（user 提出：按 provenance 划生命周期成员，待复核）
- [skill 召回率本就不高，且随 skill 数量增长而恶化](skill-recall-low-degrades-with-n.md) — `候选`（user 提出：读取率不高、越多越差，待复核）
- [直接读用户输入与 agent 输出，而非从 tool 执行反推](read-prompt-not-just-trace.md) — `候选`（user 对 ECC 抓取口的修正，待复核）
- [创建/更新/使用场景随符号留痕——为高频符号自举 per-symbol eval 预存素材](record-scenarios-for-eval.md) — `候选`（user 提出：造/改 skill 时记下凭据，参考 SkillHone；暂只记录不验证，待复核）
- [维护可脱离自积累单独成立——只维护已有 skill 不自动生成](maintenance-without-self-accumulation.md) — `候选`（user 提出：服务只想自动维护、不想自积累的用户，待复核）
- [经验沉淀后存哪一层：倾向 B 新增为 skill（参考 Hermes）、独立 instinct 层作苗圃](precipitate-storage-layer.md) — `候选`（user 取向 B：skill 可传播；正式 ADR 待开）
