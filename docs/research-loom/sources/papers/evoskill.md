# [论文] EvoSkill: Automated Skill Discovery for Multi-Agent Systems

**(authors not captured)** — [arXiv:2603.02766](https://arxiv.org/abs/2603.02766) · 2026-03 · code: [sentient-agi/EvoSkill](https://github.com/sentient-agi/EvoSkill) (~870★).

失败分析驱动的 skill 自进化（模型权重冻结，只演化 skill）：分析执行失败 → 提出新 skill 或编辑已有 skill → 物化成结构化、可复用的 skill folder。

**两端都咬 benchmark 标签**：数据集切成三份 disjoint——train 上检测失败（"失败"由标准答案判定，触发造/改 skill）、validation 上给候选打分做选择（OfficeQA 仅 17 例 ≈7%，确定性 fuzzy-match scorer 返 0/1，exact-match），test 报终值。造料端与裁决端都依赖 oracle 标签。

**"Pareto frontier" 名不副实**：摘要称 Pareto，但 Algorithm 1 实为**固定容量、单分数 top-k frontier**——保留 k 个最高 validation 分的 program，候选分数超过最弱成员才挤入，并无多目标权衡。program = system prompt + 累积 skills，每个存为一条 git branch（记 parent / generation / allowed tools / scores）。

结果：OfficeQA 60.6→67.9、SealQA 26.6→38.7；skill 从 SealQA **zero-shot 迁移**到 BrowseComp（+5.3）。

**Relevance to autoharness:** 失败→skill 的循环 + 固定容量上限（防 symbol 层膨胀）可借；但它**两端都依赖标注 benchmark**，本项目没有——属[离线评测验证](../../synthesis/offline-validation.md)的「外部 benchmark」子类，整体否决其 benchmark 依赖。（原卡"Pareto 非支配集"依摘要措辞，与全文实现的 top-k 不符，已更正。）
