---
id: offline-validation
type: direction
---
# 方向：离线评测验证 harness 更改（裁决轴 · 重）

这一族都是 **skill / harness 自进化**系统——目的都是让符号层一轮轮 update 越改越好；验证只是其中给进化把关的一环。一次 harness 编辑"算不算变好"，靠什么裁决？本大类的共性：为验证一个 update 是否正确，要在一个**评测集上离线跑一批实验**、与 agent 主运行**异步**——不是边跑边学、零额外重跑，而是专门起一轮实验来打分。这是 autoharness 的**裁决**轴，与[入料口](trace-to-experience.md)（料从哪来）、[编辑把关](../ideas/structural-gate-no-oracle.md)（准入机制）正交：同样取历史 trace，[入料口](trace-to-experience.md)把它当**候选来源**（决定「提出什么」）、本方向把它当**验证集/标尺**（决定「接不接受」），生成某候选的 trace 不得用来验证它。

按**评测集从哪来**分两子类：① 来自已有外部标注 benchmark；② 从自有历史 trace 自举。两者共担"实验开销重"，区别只在真值**外借还是自造**——也因此分别暴露于**外部依赖**与**自评偏差**。

两表均加一列 **skill 改动思路**（驱动信号 → 改动形态）。它是[入料口/提出轴](trace-to-experience.md)的横切指针——答「基于什么改、改成什么形态」，与本表主轴「接不接受」**正交**；列出只为对照各源共有的「skill 改进步」如何分叉（驱动信号尤其分裂：失败 / 打分 rollout / 成功-失败对照，并非都"基于错误"），裁决评判仍以各表的「选择·门」「我的评判」为准。

## 子类①：基于已有外部 benchmark

评测集是外部已标注数据集 + 可判定 oracle。autoharness 没有 benchmark，故**整体否决其依赖，只借循环骨架与机制**。

| 来源 | 优化对象 | skill 改动思路（驱动信号 → 改动形态） | benchmark 咬在哪端 | 选择 / 门 | 我的评判 |
|---|---|---|---|---|---|
| [kayba](../sources/github/kayba-ai-autoharness.md) | harness | 黑盒产品，自动迭代 harness（机制不公开） | 裁决端（**要你提供 benchmark command**） | benchmark 跑分 | 否决：撞名竞品，但本项目无 benchmark |
| [SkillOpt](../sources/papers/skillopt.md) | 单 skill doc（add/del/replace） | 优化器读**打分 rollout（含成功，非只失败）**→有界 add/del/replace | 裁决端（held-out 分数严格改善） | held-out 门 + 文本学习率/拒绝缓冲 | 借 held-out 门**纪律** + 编辑骨架，弃 benchmark 锚 |
| [EvoSkill](../sources/papers/evoskill.md) | system prompt + skills（存 git branch） | 分析**失败**→造新 / 改旧 skill，物化成结构化 folder | **两端**（train 判失败 + val 选择，均需 oracle 标签） | 固定容量 **top-k** frontier（摘要称 Pareto，实为单分数） | 借失败→skill 循环 + 容量上限防膨胀，弃两端标签依赖 |
| [Self-Harness](../sources/papers/self-harness.md) | harness（minimal edit） | 挖**模型特异**弱点（from traces）→驱动最小编辑 | **两端**锚 Terminal-Bench（失败 trace + held-out 通过率门） | 回归门（held-out pass rate） | 借 weakness-mine→minimal edit→regression-gate **骨架**，弃 benchmark 锚 |
| [HarnessFix](../sources/papers/harnessfix.md) | harness（7 层定位修复） | 编译 trace+harness 成 IR→LLM 反向归因定位故障层→**先诊断后改** | 失败**定义**靠外部 oracle | TargetImprovement（**再诊断**，无标签←可借）+ RegressionBound（锚 oracle） | 借 step 级归因 + 再诊断-验证半，弃 oracle 失败定义 + 7 层粗粒度 |

共同教训：候选生成廉价，**值钱的是发射前的自动 triage / 验证**；但它们把"验证"压在外部 benchmark 上，正是 autoharness 要替换掉的依赖。

## 子类②：从自有 trace 自举 eval + replay（不需外部 benchmark）

评测集从历史 trace（尤其失败）bootstrap，临时起 replay 真跑，拿"净改善（修复 > 回归）"硬信号。**autoharness 落在这条。**

| 来源 | skill 改动思路（驱动信号 → 改动形态） | eval 集来源（从 trace 怎么收） | 验证怎么跑 | 判定真值 | 实验开销 | 我的评判 |
|---|---|---|---|---|---|---|
| [RHO](../sources/papers/rho.md) | 候选编辑从多次 re-solve 的**自洽+自验证**涌现（改 CLAUDE.md/memory/脚本） | DPP 选难度多样的过往任务 coreset | 并行 **re-solve G×** → 自洽 + 自验证 | 成对**自偏好**（均值为正才采纳） | **最重**（每候选 re-solve G×） | 采纳：唯一占 benchmark-free 角的 replay；自评偏差最高（cf. [SkillLens](../sources/papers/skilllens.md) ≈46.4%），须配探索预算 |
| [MOSS](../sources/papers/moss.md) | **源码级**自重写——改文本层够不到的 code（路由/hooks/状态不变量） | 30min cron 扫生产会话挑"弱块"失败批（+ 手动 flag） | 临时 worker 上**重放失败批** | 健康探针（回滚）+ 改善度量 | 重（起临时 worker 重放） | 采纳：采集通道 + consent 换装 + 90s 健康探针回滚；勿借整源码重写 |
| [SkillGen](../sources/papers/skillgen.md) | 对照**成功 vs 失败**轨迹诱导出技能（contrastive induction） | 成功 + 失败轨迹（对照诱导） | 同实例**带/不带技能两跑** | 同计**修复 与 回归**两侧 → 净效应 | 重（每实例 2× 跑） | 采纳：干预式净效应记账，正是 gate 要的"是不是净正" |
| [SkillOpt-Sleep](../sources/github/microsoft-skillopt-sleep.md) | 承 SkillOpt 有界编辑：train 上反思 mined TaskRecords→候选 skill/memory | harvest 自有 session → mine TaskRecords（±反馈/retry 链当标签）→ train/val/test split | 每任务一个 headless `claude -p` 子进程（fresh cwd、禁 tools、候选作 **prompt text** 注入）offline replay | rule judges（regex/section/contains…）全过=1.0 / rubric judge，无人工标签 + strict-improvement 门 | 中（按 skill_hash 缓存，held-out 重评免费） | 采纳：最贴 autoharness 的工程骨架（harvest→mine→split→replay→strict gate）；caveat：测"文本在 prompt 里"≠"规则作 hook 触发的 skill"就地生效（cf. MOSS 真失败重放） |

「实验开销」一列即本子类的命门：越靠纯 benchmark-free（RHO）越通用，却越要靠多跑实验压住自评偏差。

## 界外 / 对照

按"离线跑实验验证 update"这一大类边界，下列**不入本方向**：

- **不跑 replay 实验**：darwin-skill 式（judge 共识 + test-prompts，judge 一致 ≠ 任务改善）。
- **完全不跑实验的轻量替代**：[结构化把关，不要 held-out 分数](../ideas/structural-gate-no-oracle.md)——只看结构（去重/冲突/边界）就放行，是同一问题（"接不接受"）的便宜答案，整族落在本大类**之外**（本大类定义即"要跑实验"）。但二者**组合**：先用结构门筛掉多数候选，**replay 只对过门的少数跑**，把实验开销压到可承受。
- **要防**：[探索坍缩](../sources/papers/apex.md)（重放只验旧任务 → 留显式探索预算）；[非单调遗忘](../sources/papers/self-evolving-forget.md)（回滚 + 回归门作一等公民）。
- **术语锚**："agent harness" 由 [What Makes a Harness a Harness](../sources/papers/what-makes-a-harness.md) 钉定。

## 小结

**共识**：验证 update 是否正确，都要在一个评测集上**离线跑一批实验**——有 benchmark 就直接跑分（子类①），没有就从自有 trace（尤其失败）自举 eval + replay 拿净改善硬信号（子类②）。

**两子类分歧**：评测集**外借 vs 自造**。外借（①）真值硬、自评偏差低，但依赖本项目没有的标注 benchmark；自造（②）零外部依赖、最通用，却最暴露于自评偏差（[SkillLens](../sources/papers/skilllens.md) 把上限按在 ≈46.4%）。

**代价（整族命门）**：都重——SkillOpt/EvoSkill/Self-Harness 跑 held-out、RHO 每候选 re-solve G×、MOSS 重放失败批、SkillGen 每实例 2× 跑。实验预算极易爆，故 [探索坍缩](../sources/papers/apex.md) / [非单调遗忘](../sources/papers/self-evolving-forget.md) 的回滚 + 预算封顶在此是一等公民；与轻量结构门组合是压成本的关键。

**wedge**：autoharness 取**子类②**的自举 replay，但移植**子类①**的循环骨架（weakness-mine→minimal edit→regression-gate）——把回归测试纪律套到 harness 演化：每次编辑在自有历史（尤其失败）建的 replay 集上**可验证地净改善**、且**最小/可审计/可回滚**，同时给实验预算封顶。

> **重开提示**：[动态验证生命周期](../ideas/dynamic-validation-lifecycle.md) 主张验证随交互**就地发生**、历史 eval 因**环境漂移**失效，据此把本方向从「裁决轴」降为「兜底」（只在高风险、或结构 + 动态都拿不准时动用）。该卡重开此处地位，待开决策工作表。
