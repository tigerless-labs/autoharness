# 技术选型决策记录 — 为什么以 SkillOpt 为骨架

> 决策过程记录。配合 [`DEFINITION.md`](DEFINITION.md)(产品定义)与 [`research_results/`](research_results/)(调研明细)。
> 记录:2026-06-19

---

## 决策(一句话)

**以 microsoft/SkillOpt 为落地骨架(插件壳 + ~/.claude harvest + held-out gate),从其余项目各借一个零件,没有第二个项目适合当 base。**

精度:SkillOpt 不是"绝对最成熟的工具"(ECC 212k★、GEPA 有微软采纳都更高),而是**最契合我们这条闭环的可落地骨架**——够成熟,且工程骨架直接对得上(它的 skillopt-sleep 已是现成的 Claude Code 夜间插件:harvest→mine→replay→gate→stage→adopt)。

---

## 评估维度(什么叫"可落地")

1. **代码可得**:有无公开可用实现(没有=不能 build on)。
2. **成熟度**:star / 采纳 / 是否 pip 装 / 是否已有 Claude Code 形态。
3. **问题契合**:是不是 session 驱动、动 CLAUDE.md/skills、做维护(非生成/非 prompt 优化)。
4. **判据质量 / 成本 / 耦合**:判据多硬、要不要重放、绑不绑特定框架。

---

## 评估矩阵

| 项目 | 代码 | 成熟度 | 契合我们的问题 | 作为 base? | 借什么 |
|---|---|---|---|---|---|
| **microsoft/SkillOpt** | ✅ pip | ~5.6k★,有 Claude Code 插件 | 骨架对得上(harvest/gate/插件) | ✅ **骨架** | 插件壳 + harvest + held-out gate + 安全模型 |
| Bayesian-Agent | ✅ pip | ~27★,测于 deepseek | 动作集对口,但无归因、需外部 label | ❌ | 动作集 patch/split/compress/retire + 计数置信 |
| RHO / retro-harness | ✅ | ~14★,作者单人 | 动 CLAUDE.md(最近),但判据软 | ❌ | "benchmark-free 动 CLAUDE.md"方向 + 自举纪律 |
| MOSS | ✅ | ~8★ | 源码级 whole-system,绑 OpenClaw,重 | ❌ | 失败收集渠道 + 人审热替换+回滚 控制流 |
| HarnessFix | ❌ 无代码 | 论文 | 归因(到层,非规则) | ❌ | trace-IR + step 归因 + flaw 出现率 verify(重实现) |
| SkillGen | ✅ | ~10★ | 生成器(非维护) | ❌ | 因果 repairs−regressions 净效应判据 |
| GEPA | ✅ pip | ICLR26 + 微软采纳 | prompt 优化器,需 metric,非 CLAUDE.md | ❌ | reflection-credit 归因引擎(评估借用 vs 划界) |
| ECC | ✅ | **212k★** | 增长器(无 gate),方向相反 | ❌ | 分发入口 + instincts 当输入 |
| 扫描器(AgentShield / optimize-agents-md) | ✅ | 有热度 | 静态轴一次性,非自进化闭环 | ❌ | 不同维度,不借 |
| memcli / obsidian-wiki | ✅ MIT | memcli 5★ 早期,Rust | 记忆轴(召回相关),非行为维护轴 | ❌ | **图数据模型 + `inspect` 维护面形态** |

---

## 逐个排除的理由(举例)

**Bayesian-Agent —— 排除原因:不成熟 + 缺归因。**
27★、原生测 deepseek(Claude 仅 adapter),是研究库不是产品;每个 skill 独立后验,**不做跨符号归因**,且 success/fail label 要外部 verifier。
→ 动作集 patch/split/compress/retire/explore 最对口你的目标动作,**借这个,不借整体**。

**RHO / retro-harness —— 排除原因:判据太软 + 14★ 原型。**
它动的就是 CLAUDE.md/memory/scripts(最贴),但判据是**纯成对自偏好**——自评偏差风险(SkillLens 自评 ≈46.4%),全局优化(非 per-symbol),要重放(成本);14★、作者单人,是论文原型不是可用产品。
→ 它验证了"benchmark-free 动 CLAUDE.md"这个坑存在,**借方向,不借实现**。

**MOSS —— 排除原因:太重 + 绑 OpenClaw + whole-system。**
要 Docker + 每轮重建容器 + 跑完整 coding-agent,**重写整份 TypeScript 源码**(非文件级 per-symbol 维护),且**自带 OpenClaw fork、绑死 OpenClaw**(Claude Code 只是它的编辑工具);8★。
→ 失败收集(被动扫 + 对话 flag)和安全模型(人审+90s 探针+回滚)是好参照,**借控制流,不借架构**。

**HarnessFix —— 排除原因:无公开代码 + 粒度到层不到规则。**
**没有公开实现**,build 不上去;归因到 ETCLOVG 7 层(非单条规则),LLM 归因有成本,跑在 benchmark 上(需 grader)。
→ 它的 trace-IR + step 归因方法、和"flaw 出现率降没降"这个**不需 ground-truth 的 verify**,是最值钱的两个思路,**照论文重实现并下沉到规则级**。

**SkillGen —— 排除原因:是生成器,不是维护器 + 10★。**
它造新 skill(grow),我们维护(不 grow);10★ 研究。
→ "skill=干预,净效应 = repairs − regressions(配对实例)"这个**因果判据**最严谨,**借进我们的 gate**。

**GEPA —— 排除原因:对象错(prompt)+ 需 metric。**
最成熟(微软在用、DSPy 集成、pip),但它优化**DSPy program 的 prompt**、要你**提供 metric/eval 集**,**不是 session 挖掘、不是 CLAUDE.md 原生、不是维护**。
→ 它的 reflection-credit-assignment 是工业级归因引擎,**评估借它当归因底座 vs 明确划界**(它=需 metric 的 prompt 优化,我们=session 驱动符号维护)。这是最该认真看的一个。

**ECC —— 排除原因:方向相反(增长器,无 gate)。**
212k★ 分发王,有 instincts→evolve 闭环,但**promote 靠置信/频率,没有验证净改进的 gate**,无归因、无剪枝、无执行度量——**它增长,我们维护,结构相反**。
→ **骑它**(消费其 instincts 当输入、走它的分发),它缺的 gate 正是我们的 wedge;⚠️ 时间窗:ECC 若补 gate 能用 212k★ 吃掉我们。

**扫描器(AgentShield / optimize-agents-md / audit skills) —— 排除原因:不同维度。**
静态轴、固定规则、一次性(optimize-agents-md 做压缩但手动、无 gate、无 per-symbol)。我们在反馈轴让符号随行为自进化——不是同一根轴。
→ 不借,但证明"压缩规则文件 / 审计 config"有需求,我们靠"自动+gate+归因"甩开。

**memcli / obsidian-wiki(Karpathy 那条线) —— 排除原因:记忆轴 + 太早期,但有数据模型借鉴价值。**
[memcli](https://github.com/Strawberry-Study-Group/memcli)(Rust 守护进程+CLI,本地,MIT,5★):记忆 = 带 frontmatter 的 markdown 双向链接图 + 向量,召回 = 语义+图遍历,打分 `score = similarity × weight`。
- **排除为 base 的硬伤**:① 质量信号是**召回相关性**(similarity×weight + boost/penalize 手动反馈),不是"删了任务有没有变差"——**off 我们的行为维护轴**(同 OpenClaw Dreaming);② 维护**基本手动、无 gate、无归因、无执行驱动信号**;③ 只覆盖**记忆**一个象限(不碰 rules/skills);④ Rust 栈、5★ 太早,不值得绑。
- **借什么(两点,具体)**:
  1. **数据模型** —— "linked markdown + 双向链 + weight + 图遍历"就是我们**证据规则图**的现成本地实现形态,证明这个图基底能落地。
  2. **`memcore inspect` 维护面** —— 它暴露的**近重复 / 孤儿 / 低权重**,正是我们 **$0 静态 v1** 要 surface 的 **dedup / retire 候选**;**它已 ship,证明这条 v1 方向可行**,且是现成 UX 蓝本。
- **它缺的=我们的 loop**:memcli 有"静态维护面",没有 gate + 归因 + 执行驱动 + 自动——这半正是我们补的。
- **obsidian/wiki(Karpathy 文章)同源**:"符号层=可导航链接图 + 渐进披露"的组织模式,接上 value 公式里的"注意力稀释"成本(只加载相关);但只组织、不验证/剪枝。
→ **借形态(图数据模型 + inspect 面),不绑实现**;它覆盖记忆象限、我们覆盖全符号层。

---

## 为什么 SkillOpt 赢(作为骨架)

唯一**同时**满足:① 代码可用、pip 装;② 够成熟(5.6k★);③ **已有 Claude Code 形态**(skillopt-sleep 插件:harvest ~/.claude → mine → replay → gate → stage → adopt);④ **held-out gate = 我们要的"每次更新有 eval"纪律,现成**;⑤ 安全模型(dry-run、staging、人审 adopt)对得上。

**它省掉我们重造:插件打包、session 收割、gate 纪律、安全流程。**

---

## 但 SkillOpt 是脚手架,不是解 —— 它的缺口正是我们要造的

| SkillOpt 缺 | = 我们的护城河 |
|---|---|
| 单全局文档(无 per-symbol) | 多符号 + 证据规则图 |
| 关键词判据(浅) | 纠错判据 + 无回归 + flaw 出现率 |
| 无归因 | 规则级归因(借 HarnessFix/GEPA 下沉) |
| 无适用性推断 | 执行率的分母 |
| 动作 add/delete/replace | abstract/dedup/compress/refactor/retire/hookify(借 Bayesian) |

**所以"借 SkillOpt"= 借它的壳与纪律,替换它的核(consolidate/judge/action)。** 不是 fork 了就完事。

---

## 诚实风险

1. **借壳 ≠ 借核**:SkillOpt 核心假设(单文档 + 关键词判据)伸不到多符号 + 硬判据 + 丰富动作——"扩 auto 范围"是替换核心,不是配置项,是实打实的新代码。
2. **押注集中**:竞争力压在归因 + gate 两硬点;无 ECC 的分发、无 MLflow 的成熟度兜底。
3. **GEPA 未结**:若 GEPA 的 reflection-credit 可直接当归因底座,选型还要再调(借它 vs 自建)——这一项留作待验。

---

## 结论

> **以 SkillOpt 为可落地骨架(壳 + harvest + gate + 安全),从 Bayesian(动作集)、HarnessFix(归因方法 + flaw-verify)、SkillGen(净效应判据)、MOSS(安全控制流)、GEPA(归因引擎,待评估)、ECC(分发入口)各借一块,自造四块护城河(适用性推断 / 纠错→标签 / 规则级归因 / 证据图)。其余项目因不成熟、无代码、方向相反或对象错被排除为 base,但多数贡献一个可借零件。**
