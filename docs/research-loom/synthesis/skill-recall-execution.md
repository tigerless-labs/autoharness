---
id: skill-recall-execution
type: direction
---
# 方向：skill 的召回率与执行率

一个 skill「存在」不等于它「被用」。把这条链拆成可测的三段,跨来源对齐各段被谁量过、谁没量。与 [trace 沉淀经验](trace-to-experience.md) 紧邻(那条管入料,这条管出口生效)。

## 三段链(必须分清,否则一切数字都含混)

| 段 | 机制 | 概率 | 谁在量 |
|---|---|---|---|
| **① description 注入** | 启动时全部 skill 的 name+desc 进上下文当索引 | **100% 确定** | 非问题 |
| **② 召回/触发**(正文被读 + 决定去用) | 模型据 desc 判断该不该调,才加载 body | **概率性** | ECC 自述 `~50–80%`;eval 实测 |
| **③ 执行率**(触发后真照做) | 模型把正文内容落到行为上 | **概率性** | 几乎无人单独量 |

「被使用率」指的是 **②**(条件召回 P(调用│相关)),**不是 ①**。must-always 的东西走 ② 必漏,所以 ECC 把它塞进 hook-instinct 绕开 ②——见 [hook 强制注入](../ideas/hook-forced-injection.md)。

## 各来源量到了哪一段(对齐 + 我的评判)

| 来源 | 量的是 | 段 | 性质 | 评判 | 结论(autoharness 据此做什么) |
|---|---|---|---|---|---|
| [ECC](../sources/github/affaan-m-ecc.md) | skill「fire ~50–80%」 | ② | **自述、无测量**(文档一句话,无数据) | 方向对、数字不可引 | 方向纳入;数字进 `experiments/` 自测,不写入文档 |
| 实践 eval([来源](https://thenuancedperspective.substack.com/p/agent-skills-work-but-the-research)) | 显式提示下调用率 **仅 ~70%** | ② | 单点实测,非同行评审 | 唯一落在 50–80 区间的真数 | 暂作量级锚点,待自测复现后才敢引 |
| [MetaTool](../sources/papers/metatool.md) | tool-usage awareness + selection,8 模型「难以正确选」 | ② 的代理 | 同行评审、**但在 tool benchmark 上,非 Claude Code** | 最硬的代理,非直接 | 坐实「召回是真问题」,但 skill 专属数仍须自测 |
| [SkillReducer](../sources/papers/skillreducer.md) | 55,315 skill 里 **26.4% 无 routing 描述** | ② 的上界 | 大样本实证 | 描述缺失=结构性不可召回 | 描述卫生设为**准入前置闸**(无描述不予收) |
| [Agent-Skills-data](../sources/papers/agent-skills-data.md) | 40,285 skill **intent 级冗余/同质** | ② 随 N 退化的成因 | 大样本实证 | 同质描述→路由难分→召回崩 | 结构去重/消歧列为召回**刚需**(非可选优化) |

(ACL2024 [UltraTool](https://arxiv.org/abs/2401.17167) 同测 plan→select→use 全链,可补充 ② 的代理证据。)

## 小结:空白与对 autoharness 的意义

- **直接量「Claude Code skill 触发召回率」的同行评审工作≈没有。** 学术只量代理(labeled benchmark 上的 tool selection),生态工作量的是冗余/描述质量(② 的上界与退化成因),唯一直接数来自实践 eval。**这本身是个实验机会**——`experiments/` 里自测 description 触发率,才能把 ECC 的传说变成可引证据。
- **召回是宿主原生的,我们不拥有 ② 的开关**;但**决定 ② 的东西我们能塑造**:描述卫生(SkillReducer)+ 结构化去重/消歧(Agent-Skills-data)。所以 [结构化把关](../ideas/structural-gate-no-oracle.md) 的去重/冲突闸**就是召回杠杆**——N 一大、同质描述相撞,不治理就路由崩。
- **③ 执行率几乎是研究空白**,而它正是 [滚动 curate](../ideas/adherence-driven-curate.md) 要的「被遵守/被矛盾」信号轴——触发了却没照做,等于一次「矛盾」。
