# Harness Auto-Opt — 项目定义

> 单一权威定义文件。取代已删除的 `ideas_fused.md` / `docs/ideas.md` / `docs/strategy/`。
> 调研明细见 [`research_results/`](research_results/)。工作记录,非 `docs/design/` 设计文档,不受其风格规则约束。
> 记录:2026-06-19

---

## 1. 是什么(一句话定义)

**Agent 符号层(CLAUDE.md / skills / rules / memory)的自动维护优化器:从用户的真实使用与纠错出发,把每个失败归因到负责的具体符号,在人类把关下对符号层做 abstract / dedup / compress / refactor / retire / hookify,每次更新都过验证门,产出可评审 diff 与符号健康视图——永不自动写。**

解决的问题:**符号层会膨胀、过拟合、污染决策、被忽视,而没人自动维护它。我们做维护,不做增长。**

---

## 2. 为什么(thesis)

**核心观点:** 符号层不免费。它会膨胀、过拟合 benchmark、污染决策、被 agent 忽视。真正稀缺的不是把它做大,而是自动 abstract / dedup / compress / refactor / verify / delete——**维护这个符号生态**。

**北极星(内部,对外不喊):** 符号外骨骼。冻结的权重 + 一个可读/可改/可验/可删的外部符号结构 + 经验自改进 + 人类 grounding = 能力长在权重之外、且可持续维护。这是符号学习这条 AGI 路径的维护引擎——旧符号 AI 死于维护成本与 grounding,而编码 agent 改变了维护成本曲线,使它第一次可行。

**两条纪律:**
1. **维度差异靠闭环挣来,不靠口号。** 扫描器在"静态轴"量符号当下文本;我们在"反馈轴"让符号随行为自进化。这个差异**全在闭环(归因→gated 编辑→人审)**——闭环没做成,就塌回扫描器/linter。愿景 = 把硬点做成。
2. **AGI 当北极星指方向,对外用具体痛点拉人。** 用户/HN 要的是"你的 CLAUDE.md 一半是死重、一半该转 hook,我用你自己骂过 agent 的记录证明给你看",不是 AGI 叙事。

**人在环 = grounding,不是妥协。** 纯自主自进化死于自评偏差(自偏好、糊弄验证器);人审采纳把现实信号注回回路,是这条路成立的结构性前提。

---

## 3. 第一性原理:维护 = 逐符号"估值 → 选动作"

```
value(symbol) = 相关频率 × 被遵守时的增益 − 常驻成本(token + 注意力稀释 + 冲突)
```

| 符号状态 | 动作 |
|---|---|
| 高价值 + 可机械强制 | 转 hook(保证执行 + 腾 prose 预算) |
| 高价值 + 不可强制(判断型) | 保留 |
| 和更高价值符号重叠 | dedup / merge |
| 太长相对其价值 | compress |
| 从不被遵守 / 不增益 / 纯冲突 | retire |
| 价值不确定但便宜可验 | measure |

**诚实边界:这个 value 是"该测什么的地图",不是可计算目标函数。** 精确逐符号分数现有技术算不出(相关频率/per-symbol 增益/per-symbol 稀释都是开放问题)。现有工具也都不算 value,而用阈值/增量/静态信号驱动动作。**所以产出是"带证据的动作建议",不是"精确分数+排名"。**

---

## 4. 闭环(产品管线)

```
1. 收集错误/纠错(error = 用户不满)        ← 借 SkillOpt mine 思路(负反馈短语 + LLM satisfied)
2. 归因到负责符号(谁的锅:某 skill / 某条 CLAUDE.md) ← 借 HarnessFix / GEPA 的 reflection-credit,下沉到符号粒度
   ├─ 有负责符号 → 改/删/压缩它
   └─ 无 → 审慎判断该不该新增(加硬闸,见 §8)
3. 找例子 + 合成判据                         ← 借 SkillOpt llm_miner
4. 优化 + held-out gate(每次更新有 eval)    ← 借 SkillOpt consolidate/gate
5. 产出符号健康报告 / 仪表盘 + 可评审 diff    ← 仪表盘是壳,gated diff 才是核
```

---

## 5. 判据(verify)

- **软判据 regime**(自觉接受):主信号 = **用户纠错**(比偏好客观),其次无回归,慎用偏好评分。
- **按动作分级,能多硬多硬**:dedup/compress/refactor → "行为无回归";retire → 执行率 + 删了不掉效果;hookify → 无需判据(确定性迁移);**HarnessFix 的"flaw 出现率降没降(重新归因)"= 不需 ground-truth 标签的 verify,优先用**。
- **不直接继承 SkillOpt 的关键词判据**(太浅)。
- **SWE-bench + auto-harness = 仅 demo** 证可信度,不是日常判据。
- **目标是"skill 被遵守 + 合用户意图(维护)",不是"提升编码能力(增长)"**——后者拥挤且偏离 thesis。

---

## 6. 范围

**做 code agent,Claude Code 优先。** 决定性理由不是市场,是可行性:**code 是唯一天然有客观判据(测试/diff/build)的领域**,而客观判据是 verify/性能的命根子;通用 agent 是方法最弱设定(无客观对错),会丢掉让难题可行的全部杠杆(判据、结构 trace、hooks、插件分发)。

**纪律:架构领域无关,落地按 agent 适配。** value/证据图/动作集通用;judge(测试/diff)、harvest(~/.claude)、hookify(Claude Code hooks)插件化。
排序:Claude Code → 其他 code agent(加适配器)→ 通用(最后,只搬不依赖硬判据的部分)。

---

## 7. 借什么 / 造什么

**借(别重造):**

| 能力 | 来源 |
|---|---|
| Claude Code 插件壳 + ~/.claude harvest + held-out gate(=每次更新有 eval)+ 安全模型 | SkillOpt / skillopt-sleep |
| 动作集 patch/split/compress/retire/explore | Bayesian-Agent |
| trace-IR + step 级归因方法 + "flaw 出现率"verify | HarnessFix |
| reflection-credit-assignment 归因引擎(成熟、大厂背书) | GEPA(评估借用 vs 划界) |
| 失败收集 + 人审热替换 + 回滚的控制流参照 | MOSS |
| 分发/获客入口(消费其 instincts,不拼分发) | ECC |

**造(护城河,现有工具全空白):**
0. **适用性推断**(执行率的分母,所有人共同盲区)
1. **纠错 → per-rule 标签**(定向到具体规则,非泛模式抽取)
2. **rule 级归因**(借 HarnessFix/GEPA,下沉到单条规则,非 harness 层)
3. **证据规则图 + 分诊决策**(节点=符号挂证据,边=适用/遵守/冲突/可hook,驱动逐符号判决)

---

## 8. v1 vs 完整愿景

```
完整愿景:收集 → LLM/反射归因 → 挖例子 → replay 优化 → gate → 仪表盘 + diff
  └─ $0 静态 v1 薄片:收集 → 纠错文本归因(不上 LLM trace) → dedup/hookify/粗删除/merge
                       → 可评审 diff(不 replay、不深归因、无 oracle、永不自动写、当晚出结果)
v2:加 LLM/反射 trace 归因 + replay 优化 + 性能维度(SWE-bench demo)
```

**v1 只做信号廉价可算的动作**(冗余/可强制性/token/presence),给"动作建议 + 证据",不给精确分数。

**三个硬点(成败关键,非细节):**
1. **归因到具体符号**——HarnessFix 只到 7 层,你要到几十条规则,细且噪。先用纠错文本显式指向(便宜准),够不到再上 LLM trace 归因。**第一步:拿自己 5 条真实纠错手验"能否稳定归到具体规则"。归不准,整条线塌。**
2. **"该不该新增"= 增长闸**——新增是最后手段,须同时满足:复现 ≥N 次、现有符号 merge 不进、过 gate。否则退化成 ECC(增长器)。
3. **判据深度**——别只用关键词;用纠错判据 + 无回归 + flaw 出现率。

---

## 9. 竞争定位

| 对手 | 它是什么 | 我们的关系 |
|---|---|---|
| **MLflow** | eval-time 验证器(手写测试,适用性你声明) | 不同品类;它是上游零件;**别把自己降级成 eval 工具** |
| **ECC**(212k★) | 增长器(extract→promote,无 gate) | 相反方向;我们是它缺的 gate+归因+剪枝;**骑它别拼分发**;⚠️ ECC 若加 gate 能用分发吃掉我们——**时间窗** |
| **SkillOpt-Sleep** | 单全局文档优化,关键词判据 | 借其壳/gate;我们 per-symbol + 归因 + 硬判据 |
| **GEPA**(ICLR26,MS 在用) | reflection-credit prompt 优化器(需 metric+DSPy) | **最该认真看**:借其归因引擎 vs 划界(它=prompt 优化,我们=session 驱动符号维护) |
| **扫描器**(AgentShield / optimize-agents-md / audit skills) | 静态轴:固定规则量当下文本,一次性 | **不同维度**:我们在反馈轴让符号自进化 |

**唯一空白(护城河):真实 session、per-symbol、归因驱动的维护闭环。** 没人做 measure→归因→修→gate→diff 的闭环。

**诚实风险:** 竞争力全押在归因+gate 两硬点;而我们无 ECC 的分发、无 MLflow 的成熟度兜底——硬点没做成则既无壁垒又无退路。

---

## 10. 命名

内部代号 **Harness Auto-Opt**。⚠️ 撞三个 ~300★ repo(aiming-lab 治理 / parikhakshat fuzzing / kayba 需-benchmark 优化器)+ AutoHarness 论文。**对外名/第一句必须划清界限**:benchmark-free、生产轨迹自举、per-symbol 维护(kayba 不覆盖、只 14★ 的 retro-harness 占着的坑)。
