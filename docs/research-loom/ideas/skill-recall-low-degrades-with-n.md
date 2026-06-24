---
id: skill-recall-low-degrades-with-n
type: idea
status: 候选
---
# skill 的召回率本就不高,且随 skill 数量增长而进一步恶化

**主张**:一个 skill「存在」远不等于它「被读、被用」。把使用拆成三段(① desc 注入 100% → ② 召回/触发 概率性 → ③ 执行 概率性,见 [skill 的召回率与执行率](../synthesis/skill-recall-execution.md))后,真正决定「被用」的 **② 召回率本就不高**:唯一的直接实测里,即便**显式提示**该用某 skill,调用率也只有 **~70%**;ECC 自述的 `~50–80%` 落在同一量级。更要紧的是**这条曲线随 skill 总数 N 单调下行**——N 越大,召回越差,原因是结构性的:

1. **同质/冗余描述相撞,路由无从分辨。** 大样本实证里 40,285 个 skill 存在 intent 级的冗余同质([Agent-Skills-data](../sources/papers/agent-skills-data.md));描述彼此难分,模型在「该调哪个」上就崩。
2. **描述缺失直接判死。** 55,315 个 skill 中 **26.4% 根本没有 routing 描述**([SkillReducer](../sources/papers/skillreducer.md))——这部分结构性不可召回,N 里掺得越多,可召回比例越低。
3. **选择本身是已被证伪的难点。** 8 个模型在 tool selection 上「难以正确选」([MetaTool](../sources/papers/metatool.md));候选集越大,选错概率越高。

所以「skill 多多益善」是错觉:**加一个边际 skill,既摊薄注入预算、又往候选池里多塞一个会被混淆的对象,把存量 skill 的召回也一起拖低**。召回不是随 N 持平,而是随 N 退化。

**对 autoharness 的意义。** 维护层的价值不在「攒得多」,而在**压低 N 的同时治理 N**:① 描述卫生设为准入前置闸(无描述/同质描述不予收),② 结构化去重与消歧是召回刚需而非可选优化(见 [结构化把关](structural-gate-no-oracle.md))。「少而精」对召回是正收益,「多而全」是负收益——这给 [滚动 curate](adherence-driven-curate.md) 的「定生死」提供了方向:删冗余 skill 不只是省空间,是直接抬升存量召回。

## 论据 / 出处

蒸馏自方向卡 [skill 的召回率与执行率](../synthesis/skill-recall-execution.md) 的对齐结论:② 的量级锚点来自实践 eval(显式提示下 ~70%,[来源](https://thenuancedperspective.substack.com/p/agent-skills-work-but-the-research))与 [ECC](../sources/github/affaan-m-ecc.md) 自述(~50–80%,无测量);随 N 退化的三条成因分别坐实于 [Agent-Skills-data](../sources/papers/agent-skills-data.md)(同质冗余)、[SkillReducer](../sources/papers/skillreducer.md)(26.4% 无描述)、[MetaTool](../sources/papers/metatool.md)(selection 难)。直接量「Claude Code skill 触发召回率」的同行评审工作≈没有——量级须由 `experiments/` 自测复现后才敢正式引证。

## 待解 / 边界

- **数字暂不可引。** ~70% / ~50–80% 是单点实测与自述,作量级锚点;退化曲线的斜率(N 每增一个,召回掉多少)更是无人量过。须 `experiments/` 自测 description 触发率随 N 变化,才能从「传说」变证据。
- **「越多越差」是趋势而非绝对**:良好治理(描述彼此正交、零冗余)能拉平曲线;命题精确表述应是「未经治理时,召回随 N 退化」,治理正是 autoharness 要做的事。

## 关联

蒸馏自 [skill 的召回率与执行率](../synthesis/skill-recall-execution.md);为 [结构化把关](structural-gate-no-oracle.md)(去重/消歧=召回杠杆)与 [滚动 curate](adherence-driven-curate.md)(删冗余=抬召回)提供动机轴;与 [hook 强制注入](hook-forced-injection.md)(对 must-always 规则绕开 ② 的另一条路)互补。将装配进 [design/](../design/index.md) 的 Admission/Curate 段。
