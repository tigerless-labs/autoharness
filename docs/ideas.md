# Ideas & 决策记录

工作记录,非设计文档 - 不受 `docs/design/` 风格规则约束。记录产品想法、问题陈述、待验证的 HN/社区提问。

---

## Idea 001 — 带验证门的 skill / CLAUDE.md 瘦身器(skill-library compressor with a gate)

*记录于 2026-06-17*

### 问题(the problem)

市面上 code skill / agent skill 越来越火,但它们都**很重**:

- 一份 `CLAUDE.md` 加上 `.claude/rules/`、记忆、项目指令,**用户没说话就先吃掉 20-30K token**(见 [anthropics/claude-code#33464](https://github.com/anthropics/claude-code/issues/33464))。
- skill 不是越多越好:**skill 过载会让 agent 幻觉、烧钱、抓错工具**(写邮件时被 calendar skill 的说明带偏)。
- **选择与适配困难**:面对一堆现成 skill 包(superpowers / ECC / anthropics/skills...),用户不知道哪些对自己有用,装上后也不知道哪些在拖后腿。
- 现有的「审计 / 精简」全靠人手——「每个上下文留 5-8 个工具、定期审计、SKILL.md 控制在 5000 字内」是人肉纪律,没有自动化。

**一句话:符号层(skill/harness/记忆)不免费;它会膨胀、过拟合、污染决策。真正稀缺的不是「把它做大」,而是「自动 abstract / dedup / compress / refactor / verify / delete」——维护这个符号生态。**

### 思想根基:符号学习的文艺复兴(symbolic learning)

来源:知乎 Eddy《符号学习在 Agent 时代的文艺复兴?》+ 本仓库 `docs/research_results/symbolic-learning-framing.md`。

- **符号 = 离散、可复用、可组合、有 grounding 的句柄,压缩了「行动相关的不变量」**。好的压缩 = 智能(MDL / Kolmogorov / Solomonoff 谱系)。
- 两条学习路线对照:
  - 深度学习:`经验 → 梯度 → 权重`
  - 符号学习:`经验 → 反思/搜索/编辑 → 符号产物`(skill / 代码 / 测试 / 记忆 / harness)
- 旧符号 AI 失败不是因为符号错,而是**维护成本**(grounding、开放世界、规则库技术债)。现在的赌注:**编码 agent 改变了符号系统的维护成本曲线**。
- 三个代表作:Heuristic Learning(把 RL 循环从权重空间搬到软件空间)、AutoHarness(符号层 = agent 行动边界)、SkillOpt(符号空间里的梯度下降)。
- **关键警示(本 idea 的立足点)**:符号层会 skill 膨胀、harness 过拟合 benchmark、记忆污染决策、agent 糊弄验证器。**稀缺能力是维护,不是增长。**

### 市场缺口(2026-06-17 复核)

| 层 | 状态 |
|---|---|
| 运行时**会话上下文**压缩 | 🔴 已红海 - [Ruya-AI/cozempic](https://github.com/Ruya-AI/cozempic)(338★, 150k+ 下载)、[nicobailon/cc-prune](https://github.com/nicobailon/cc-prune)、[NodeNestor/claude-rolling-context](https://github.com/NodeNestor/claude-rolling-context)、Opencode-DCP→Sleev |
| 磁盘上 **skill 库 / CLAUDE.md** 自动瘦身 | 🟡 只有手工技巧([johnlindquist gist](https://gist.github.com/johnlindquist/849b813e76039a908d962b2f0923dc9a),初始 token 砍 54%),无产品 |
| **瘦身 + 验证门**(砍完用自己的轨迹证明没掉分) | 🟢 **空白** - 没人做 |

「压缩 / retire」在论文里只是子动作:Bayesian-Agent 的 `patch/split/compress/retire/explore` 动作集最接近,但没人把「瘦身」做成带门的独立产品。

### 想法(the idea)

一个 **dream 插件**(夜间离线,类似 SkillOpt-Sleep 的 `/sleep`),基于 **replay set**:

1. 从用户自己的会话轨迹 / 重复纠错里,建一个**「你自己的问题」replay set**(纠错信号是廉价金标签,绕开自评偏差)。
2. 从一个**策展目录**(先用信任的几个 skill 包,不开放互联网自动安装——那是安全雷)匹配候选 skill 到用户的问题。
3. 对每个候选 / 每条现有 skill,**过 replay 门**:装上/保留它,在 replay set 上**净改进吗?**(repairs > regressions)。只留赢家,retire 拖后腿的。
4. 把留下的**裁瘦**到「对你够用」的最小形态。
5. 输出一份个性化、最小的 harness + `CLAUDE.md`,**可评审 diff**,人审后采纳——绝不自动写。

**护城河 = 那道门**(用自己历史轨迹自举验证净改进,免基准)。**轻在接入**(零配置、插件、第一晚出 diff),**不轻在技术**(门是命根子,不能砍)。省 token 靠工程:极小 coreset 重放、夜间离线、便宜启发式先过滤候选。

**v2(以后,opt-in,默认关):** 自动上网发现**新** skill,套重护栏(沙箱 replay、永不自动安装、来源校验、人审)。

### 待办 / 下一步

- [ ] 决定本 idea 是否升级为正式方向 → 写进 `STRATEGY.md` 或 `docs/design/`
- [ ] HN 提问验证需求(见下)
- [ ] 名字冲突:`AutoHarness` 撞三个 ~300★ repo(治理 / fuzzing / 需基准的优化器),宣传第一句须划清界限或换名

### HN 提问草稿(Ask HN, 发出去验证需求)

> **Ask HN: Do your AI coding agent's skills / CLAUDE.md get too heavy — and how do you prune them?**
>
> I keep hitting the same wall with Claude Code / Codex-style agents: my `CLAUDE.md`, `.claude/rules/`, skill files, and memory keep growing until 20-30K tokens are spent before I type anything. Worse, having *more* skills seems to make the agent dumber — it gets distracted by an irrelevant skill, hallucinates, or picks the wrong tool.
>
> There are great tools now for trimming the *runtime session* (cozempic, cc-prune, rolling-context, Sleev). But I haven't found anything that trims the *skills/CLAUDE.md themselves* — and, critically, that can **prove a cut didn't make the agent worse**. Right now "audit your skills" is purely manual.
>
> The idea I'm toying with: a nightly offline pass that builds a small replay set from my own past sessions (especially the ones where I corrected the agent), then for each skill asks "does keeping/adding this net-improve on my replay set?" — keep the winners, retire the dead weight, slim what's left, and hand me a diff to approve. Benchmark-free, gated on my own trajectories, never auto-applied.
>
> Questions for you:
> 1. Do you actually feel skill/instruction bloat, or is progressive disclosure enough in practice?
> 2. How do you decide which skills/rules to cut today? Gut feel, or something measurable?
> 3. Does anything already exist that *verifies* a skill change is net-positive (not just "it ran")?
> 4. Would you trust a tool to propose deletions from your CLAUDE.md if it showed you a gated before/after on your own task history?
>
> Not selling anything — trying to figure out if this is a real pain or just mine.
