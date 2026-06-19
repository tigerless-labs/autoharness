# Ideas & 决策记录

工作记录，非设计文档；不受 `docs/design/` 风格规则约束。用于记录产品想法、问题陈述、待验证的社区提问和阶段性决策依据。

---

## Idea 001 — 带验证门的 skill / CLAUDE.md 瘦身器

**英文暂名：** SkillPatch Gate / Skill Library Compressor with a Gate  
**状态：** 建议作为正式候选方向进入策略层记录，先通过最小 MVP 验证，再决定是否进入 `docs/design/`。  
**记录时间：** 2026-06-17；2026-06-18 更新

---

## 0. 当前判断

这个方向的主线是：**维护 coding agent 的符号层，而不是继续堆更多 skill / rule / memory。**

更具体地说，它不是一个单纯的 skill 生成器，也不是一个泛泛的 AutoHarness 框架，而是一个面向 Codex / Claude Code / Cursor 等 coding agent 用户的轻量工具：

> 从用户自己的历史 session、重复纠错、rules 文件、skills、`CLAUDE.md` / `AGENTS.md` 中抽取可验证信号，生成可评审 diff，并用 replay / rule gate 证明这次瘦身、保留、删除或迁移没有让 agent 变差。

Idea 001 可以自然拆成三个工程子模块：

| 子模块 | 作用 | 和主线的关系 |
|---|---|---|
| **001-A Rule Execution Gate** | 验证 rules / skills 有没有真的执行，以及修改后执行率有没有提升 | 核心验证门 |
| **001-B Correction Memory Compiler** | 从用户纠正中提取稳定学习信号，沉淀为 rule / skill / eval / guardrail | 学习信号入口 |
| **001-C Rules Porter** | 统一和迁移 `AGENTS.md` / `CLAUDE.md` / Cursor rules / Copilot instructions 等规则文件 | 输入整理层 |

这三个子模块分别对应主线中的三个关键问题：

- **规则在哪里、是否重复、能否统一：** 由 Rules Porter 处理。
- **历史坏记录和用户纠正如何变成可维护符号：** 由 Correction Memory Compiler 处理。
- **规则和 skill 修改后是否真的更好：** 由 Rule Execution Gate 处理。

因此，完整流程不是“生成更多 skill”，而是：先整理规则来源，再抽取纠错信号，最后用验证门筛选可接受的瘦身或补丁方案。

---

## 1. 问题（the problem）

市面上 code skill / agent skill 越来越火，但它们都**很重**。

- 一份 `CLAUDE.md` 加上 `.claude/rules/`、记忆、项目指令，用户没说话就可能先吃掉大量 token。Claude Code issue #52979 中有用户反馈，在空目录、无 repo、无 `CLAUDE.md` 的简单 prompt 下仍出现约 19k–31k token 的固定开销。  
  证据：https://github.com/anthropics/claude-code/issues/52979
- Claude Code issue #33464 中有用户反馈，`CLAUDE.md`、rules files、project instructions 会在 session 启动时进入上下文，随着这些文件增长，它们会与工作记忆竞争上下文空间。  
  证据：https://github.com/anthropics/claude-code/issues/33464
- Claude Code issue #44536 中有用户提出 lazy context loading 需求，问题陈述中明确提到启动时加载 `CLAUDE.md`、memory、MCP servers、skills、rules、tool definitions 等上下文，并给出不同组件的 token 开销估算。  
  证据：https://github.com/anthropics/claude-code/issues/44536
- Claude Code 官方文档说明，Claude Code 会从项目目录和 `~/.claude` 读取 instructions、settings、skills、subagents、memory 等内容；memory 文档也说明 `CLAUDE.md` 和 auto memory 都会作为 context 加载到每个会话中，而不是强制执行的配置。  
  证据：https://code.claude.com/docs/en/claude-directory  
  证据：https://code.claude.com/docs/en/memory
- `AGENTS.md` / `CLAUDE.md` 配置文件的研究指出，Context Bloat、Skill Leakage、Conflicting Instructions 等 smell 广泛存在；该研究分析了 100 个包含 `AGENTS.md` 或 `CLAUDE.md` 的热门开源仓库，发现 Lint Leakage、Context Bloat、Skill Leakage 是较常见问题。  
  证据：https://arxiv.org/abs/2606.15828

用户可以不断给 agent 加规则、加 memory、加 skills，但很少有工具能回答：

- 哪些规则真的被执行了？
- 哪些 skill 在拖后腿？
- 哪些内容只是重复、过期或过长？
- 删掉一段 `CLAUDE.md` 后，agent 有没有变差？
- 历史纠正应该变成 rule、skill、eval，还是应该丢弃？

一句话：

> **符号层（skill / harness / rules / memory）不免费；它会膨胀、过拟合、污染决策。真正稀缺的不是继续把它做大，而是自动 abstract / dedup / compress / refactor / verify / delete，也就是维护这个符号生态。**

---

## 2. 思想根基：符号学习的文艺复兴（symbolic learning）

本方向的核心假设是：

> 未来 coding agent 的提升，不只来自更强模型，也来自更好的外部符号层维护。

这里的“符号”指的是离散、可复用、可组合、有 grounding 的操作句柄，例如：

- `AGENTS.md`
- `CLAUDE.md`
- `.claude/skills/*/SKILL.md`
- `.cursor/rules/*`
- workflow rules
- hooks
- eval cases
- replay tasks
- memory entries
- guardrails

两条学习路线可以这样对照：

| 路线 | 训练对象 | 更新方式 |
|---|---|---|
| 深度学习 | 模型权重 | 经验 → 梯度 → 权重 |
| 符号学习 / text-space learning | prompt / skill / rules / harness | 经验 → 反思 / 搜索 / 编辑 → 符号产物 |

这里不是传统 BP 反向传播，也不是更新 LLM 内部参数。更准确地说，这是 **冻结模型 + 外部文本状态优化**。

相关工作已经提供了直接证据：

- SkillOpt 将自然语言 skill 作为 frozen LLM agent 的外部可训练状态，通过 trajectory-driven edits、validation-gated updates 产出可部署的 `best_skill.md`。  
  证据：https://github.com/microsoft/SkillOpt  
  证据：https://arxiv.org/abs/2605.23904
- TextGrad 使用 LLM 提供的自然语言反馈作为 textual gradients，将反馈传播到复合 AI 系统的可优化组件。这里的“gradient”是自然语言反馈，不是传统数值梯度。  
  证据：https://arxiv.org/abs/2406.07496  
  证据：https://github.com/zou-group/textgrad

本方向的立足点不是“让符号层无限增长”，而是相反：

> 符号层会 skill 膨胀、harness 过拟合、记忆污染决策、agent 糊弄验证器。稀缺能力是维护，不是增长。

---

## 3. 相关工作与市场缺口

### 3.1 运行时会话上下文压缩已经比较拥挤

运行时 session/context 压缩已经出现较多项目，例如：

- Cozempic：Claude Code context cleaning / pruning。  
  证据：https://github.com/Ruya-AI/cozempic
- claude-rolling-context：通过代理做 rolling context compression。  
  证据：https://github.com/NodeNestor/claude-rolling-context
- context-mode：通过 sandbox 处理大输出，只把摘要放进上下文。  
  证据：https://github.com/mksglu/context-mode

因此，如果只做“运行时上下文压缩”，容易进入拥挤方向。

### 3.2 skill / CLAUDE.md 磁盘层维护仍有缺口

已有很多 issue、文章、社区经验在讨论如何压缩 `CLAUDE.md`、skills、rules，但“自动瘦身 + 验证门”的独立工具仍没有明显成熟方案。

需要谨慎表述：不能说完全没人做相关事。SkillOpt 已经非常接近“从轨迹训练自然语言 skill”的方向，并且包含验证门思想。  
证据：https://github.com/microsoft/SkillOpt

可切入空隙是：

> 不做完整 SkillOpt 级别的 skill optimizer，而是做更轻量的 “skill / CLAUDE.md compressor with a gate”：专注于已有本地 skill/rules 的去重、瘦身、retire、可评审 diff，并用用户自己的小 replay set 证明净改进。

### 3.3 rules / manifests 生态正在扩张

AGENTS.md 已经被定位为指导 coding agents 的开放格式，官网称其已被 60k+ open-source projects 使用。  
证据：https://agents.md/

真实生态里还存在多种配置格式，例如 `CLAUDE.md`、`AGENTS.md`、`GEMINI.md`、`copilot-instructions.md`、Cursor rules、Windsurf rules 等。  
证据：https://www.deployhq.com/blog/ai-coding-config-files-guide

这说明 rules porter 不是凭空想象，而是多 agent 生态下的真实维护问题。

### 3.4 rules 是否真的执行，已经是可验证问题

promptfoo 已支持 coding-agent eval，覆盖 OpenAI Codex SDK、OpenAI Codex app-server、Claude Agent SDK、OpenCode SDK 等。  
证据：https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/

promptfoo 的 agent skills 测试文档还提到，可以通过 first-class skill tool calls 或 trace evidence 判断 skill 是否被调用。  
证据：https://www.promptfoo.dev/docs/guides/test-agent-skills/

这说明“验证 coding agent 行为”已有基础设施。当前缺口不是重新发明 eval 框架，而是：

> 从 `AGENTS.md` / `CLAUDE.md` / skills 中自动抽取 rules，生成 rule execution checks / replay cases，回答“这些规则是否真的被执行”。

---

## 4. 想法（the idea）

做一个 **带验证门的 skill / CLAUDE.md 瘦身器**，可以理解为一个 nightly offline / dream 插件。

核心流程：

1. **Collect：** 从用户自己的会话轨迹、重复纠错、失败记录、rules 文件、skills 中收集信号。
2. **Compile：** 把重复纠错、失败模式、规则执行证据整理成结构化候选。
3. **Patch：** 对 skill / `CLAUDE.md` / `AGENTS.md` 生成候选补丁，包括 add / delete / replace / compress / retire。
4. **Gate：** 用用户自己的 replay set 或 rule execution checks 验证候选修改是否净改进。
5. **Review：** 输出个性化、最小化的 harness / skill / `CLAUDE.md` diff，由人审后采纳，绝不自动写。

关键原则：

- 默认本地离线运行。
- 默认 dry-run，不自动改用户项目。
- 每个修改都要附 evidence link，说明来自哪段 session / 哪次纠正 / 哪条规则。
- 不开放互联网自动安装 skill。后续如果支持外部 skill 发现，必须 opt-in、来源校验、沙箱 replay、人审。
- 真正的护城河不是“能生成 skill”，而是“能证明保留 / 删除 / 压缩后没有让用户自己的任务变差”。

---

## 5. 子模块 001-A — Rule Execution Gate

### 问题

用户写了很多 rules，但不知道 agent 到底有没有执行。

典型规则包括：

- 修改代码后必须跑测试。
- 不要修改 generated 文件。
- 不要改 lockfile，除非任务明确要求。
- 提交前必须总结 diff。
- 遇到 schema 变更先询问用户。
- 修改 API 后必须运行 `npm run test:api`。

这些规则写进 `AGENTS.md` / `CLAUDE.md` / `SKILL.md` 后，真实运行时仍可能发生：

- agent 忘记执行；
- agent 只在总结里声称执行，但实际上没有跑；
- agent 在简单任务里遵守，复杂任务里失效；
- 修改规则后，用户不知道执行率是否提高；
- 精简 skill / `CLAUDE.md` 后，不知道有没有删掉关键行为。

一句话：

> **现在用户能写 rules，但缺少一个机制证明这些 rules 在真实任务里是否被执行。**

### 想法

做一个 rule execution gate，从 rules 中抽取可验证项，并基于历史 session / replay set 计算执行证据。

示例：

```text
规则：修改 API 后必须运行 npm run test:api

before: 3/10 次执行
candidate patch: 在 API skill 中加入明确测试步骤
after: 8/10 次执行
regression: 1 次
net improvement: +4
decision: accept / pending review
```

### 和主线的关系

Rule Execution Gate 是 SkillPatch Gate 的核心验证门。要证明 skill / `CLAUDE.md` 的瘦身、保留、删除是否净改进，就必须回答：

1. 规则有没有被执行？
2. 修改后执行率有没有增长？
3. repairs 是否大于 regressions？

### MVP

第一版先支持最容易验证的规则类型：

| 规则类型 | 验证方式 |
|---|---|
| must-run command | 检查 session / terminal log 是否出现指定命令 |
| must-not-touch files | 检查 git diff 是否修改 forbidden paths |
| output format | 检查最终回复是否包含指定结构 |
| must-ask-before | 检查是否先出现用户确认 |
| must-read-file | 检查工具调用 / transcript 是否读取指定文件 |

命令草案：

```bash
skillpatch rule extract --from AGENTS.md
skillpatch rule scan-history --from ~/.codex/sessions
skillpatch rule gate --before old.md --after new.md
skillpatch rule report
```

第一阶段不必真的重跑 agent，可以先做 **evidence check**：

- 从 transcript / command log / git diff / tool events 里判断 rule 是否曾经执行；
- 对新 patch 做静态检查和人工 review；
- 第二阶段再引入 before / after replay。

---

## 6. 子模块 001-B — Correction Memory Compiler

### 问题

用户在和 coding agent 协作时，会不断纠正 agent：

```text
你又没跑测试。
不要改 generated 文件。
不要直接动 package-lock.json。
这个项目先看 docs/design.md。
这个错误之前已经说过了。
以后提交前先总结影响范围。
```

这些纠正常常是最有价值的学习信号，但通常散落在聊天历史里，没有系统性沉淀。

结果是：

- 同样错误下次还会发生；
- 用户重复教育 agent；
- 有价值的纠正没有进入 `AGENTS.md` / skill / eval；
- memory 越来越杂，但真正可执行规则没有变多；
- 长期协作经验没有变成稳定的 harness 资产。

一句话：

> **用户纠正是廉价金标签，但现在缺少一个轻量工具把它编译成可维护的 rules / skills / evals / guardrails。**

### 想法

做一个 correction memory compiler，把用户纠正先放入 staging，再分流到不同目标：

| 纠正类型 | 应沉淀目标 |
|---|---|
| 项目固定规则 | `AGENTS.md` / `CLAUDE.md` |
| 可复用流程 | `SKILL.md` |
| 可验证行为 | eval case / replay task |
| 安全边界 | guardrail |
| 一次性偏好 | memory |
| 噪声 / 过期内容 | discard |

示例：

```text
纠正：以后不要直接改 package-lock.json，除非明确要求升级依赖。

编译结果：
类型：guardrail + project rule
目标：AGENTS.md
规则：Do not modify lockfiles unless the task explicitly involves dependency changes.
验证：生成 no-lockfile-edit replay case
```

### 和主线的关系

Correction Memory Compiler 是 SkillPatch Gate 的学习信号入口。SkillPatch Gate 需要从用户自己的历史轨迹和重复纠错里构建 replay set，而 Correction Memory Compiler 负责把非结构化纠错变成结构化候选。

它的边界不是做一个长期记忆系统，而是：

> 重复纠错先进入 staging，再判断应该变成 rule、skill、eval、guardrail 还是丢弃。

### MVP

命令草案：

```bash
skillpatch corrections scan ~/.codex/sessions
skillpatch corrections inbox
skillpatch corrections promote --to rule
skillpatch corrections promote --to skill
skillpatch corrections promote --to eval
```

输出：

```text
.skillpatch/corrections/inbox.md
.skillpatch/corrections/classified.json
.skillpatch/patches/agents-rule.diff
.skillpatch/skills/api-workflow/SKILL.md
.skillpatch/evals/no-lockfile-edit.yaml
```

关键机制：

- staging first；
- human review；
- evidence link；
- never auto-apply；
- 明确区分长期规则和一次性偏好。

---

## 7. 子模块 001-C — Rules Porter

### 问题

多 agent 生态正在变得分裂。用户可能同时使用 Codex、Claude Code、Cursor、GitHub Copilot、Gemini CLI、OpenCode 等工具，每个工具都有自己的规则文件和加载方式：

```text
AGENTS.md
CLAUDE.md
.cursor/rules/
.github/copilot-instructions.md
GEMINI.md
.claude/skills/
```

结果是：

- 同一套项目规则要维护多份；
- 不同工具之间规则不同步；
- 有些规则在一个 agent 里生效，另一个 agent 里没有；
- 用户迁移工具时不知道怎么搬规则；
- 规则越积越多，重复、冲突、过期。

AGENTS.md 已经尝试成为一个开放标准，但真实项目里仍然存在多种格式并存。  
证据：https://agents.md/  
证据：https://www.deployhq.com/blog/ai-coding-config-files-guide

### 想法

做一个 rules porter / rules migration tool。

它扫描用户项目里的 `AGENTS.md`、`CLAUDE.md`、Cursor rules、Copilot instructions、Gemini rules 等文件，输出：

1. 当前项目有哪些规则文件；
2. 哪些规则重复；
3. 哪些规则只存在于某一个 agent 配置里；
4. 哪些规则格式不兼容；
5. 如何生成 source-of-truth；
6. 如何导出到不同 agent 目标格式；
7. 输出 reviewable diff，而不是直接覆盖用户文件。

### 和主线的关系

Rules Porter 是 SkillPatch Gate 的输入整理层。

在做 skill / `CLAUDE.md` 瘦身前，需要先知道用户到底有哪些规则文件，哪些重复，哪些只存在于某个 agent 里，哪些应该统一到 canonical source。

合理流程是：

```text
Rules Porter 整理多端规则
→ Correction Compiler 抽取历史纠错
→ Rule Execution Gate 验证规则执行
→ Skill / CLAUDE.md Compressor 生成瘦身 diff
```

### MVP

命令草案：

```bash
skillpatch rules scan
skillpatch rules compare
skillpatch rules convert --to claude,codex,cursor,copilot,gemini
skillpatch rules diff
```

核心模块：

```text
sources/
  agents_md.py
  claude_md.py
  cursor_rules.py
  copilot_instructions.py
  gemini_md.py

analyzers/
  duplicate_detector.py
  conflict_detector.py
  portability_checker.py

generators/
  claude_md_generator.py
  agents_md_generator.py
  cursor_rules_generator.py
  copilot_generator.py

outputs/
  compatibility_report.md
  patches/*.diff
```

第一版主要是文件解析、模板生成、重复检测和 diff 输出，不需要完整 LLM 训练，也不需要跑 agent。

### 相关工作边界

wshobson/agents 已经做了 multi-harness agentic plugin marketplace，并强调 one source-of-truth 到多个 harness 的 native artifacts。  
证据：https://github.com/wshobson/agents

因此本模块不能做 marketplace，而应该只做用户已有项目的 rules migration / compatibility / dedup。

---

## 8. 模块层级关系

```text
SkillPatch Gate / 带验证门的 skill / CLAUDE.md 瘦身器
│
├── 001-A Rule Execution Gate
│   └── 核心验证门：规则是否执行？修改后执行率是否提升？
│
├── 001-B Correction Memory Compiler
│   └── 学习信号入口：用户纠正如何变成 rule / skill / eval / guardrail？
│
└── 001-C Rules Porter
    └── 输入整理层：多 agent 规则如何统一、迁移、去重？
```

三个子模块和主线关系如下：

- **Rules Porter** 解决“规则在哪里、怎么统一”的问题；
- **Correction Memory Compiler** 解决“历史坏记录 / 用户纠正如何变成可维护符号”的问题；
- **Rule Execution Gate** 解决“规则有没有真的执行、是否净改进”的问题；
- **SkillPatch Gate** 把三者串成一个可落地闭环，最终做 skill / `CLAUDE.md` 的瘦身、保留、删除和验证。

---

## 9. 工程落地路线

### Phase 0 — evidence-only report

目标：先证明问题存在，不改任何文件。

功能：

- 扫描本地 `AGENTS.md` / `CLAUDE.md` / skills / rules；
- 统计 token / 字数 / 重复段落；
- 抽取可验证 rules；
- 从历史 session 中提取用户纠正；
- 输出一份 `report.md`。

### Phase 1 — reviewable diff

目标：生成候选补丁，但不自动应用。

功能：

- 生成 `CLAUDE.md` / `AGENTS.md` 的瘦身 diff；
- 生成 `SKILL.md` 的 compress / retire 建议；
- 生成 rule execution checks；
- 每个修改附 evidence。

### Phase 2 — light gate

目标：对候选 diff 做轻量验证。

功能：

- 检查 must-run command 是否执行；
- 检查 forbidden paths 是否被修改；
- 检查 output format 是否满足；
- 计算 rule execution rate；
- 输出 repairs / regressions。

### Phase 3 — replay gate

目标：真正用用户自己的 replay set 判断 net improvement。

功能：

- 从历史失败构建小型 replay set；
- 对 before / after skill 或 rules 进行 replay；
- 只接受净改进的 patch；
- 未确认 patch 进入 pending review。

---

## 10. 待办解决方案

### 待办一：是否升级为正式方向

**结论：建议升级为正式候选方向，但先进入 `STRATEGY.md` 或 `docs/strategy/skillpatch-gate.md`，不要直接进入 `docs/design/`。**

依据如下：

1. **问题有外部证据。** Claude Code token/context bloat、`CLAUDE.md` / rules / memory 加载成本、配置 smell 已经有 GitHub issue、官方文档和论文支撑。  
   证据：https://github.com/anthropics/claude-code/issues/33464  
   证据：https://github.com/anthropics/claude-code/issues/52979  
   证据：https://github.com/anthropics/claude-code/issues/44536  
   证据：https://code.claude.com/docs/en/memory  
   证据：https://arxiv.org/abs/2606.15828
2. **方向有研究依据。** SkillOpt 证明 skill 可以作为 frozen agent 的外部可训练状态，通过 bounded edits 和 validation gate 优化。  
   证据：https://github.com/microsoft/SkillOpt  
   证据：https://arxiv.org/abs/2605.23904
3. **工程切口足够轻。** 本方向不复刻完整 SkillOpt / Trace2Skill / RHO，而是先做本地 skill/rules maintenance、reviewable diff、light gate 和 report，更适合先做开源 MVP。

暂不直接进入 `docs/design/` 的原因：

- extraction、diff、rule gate 仍需要通过最小 demo 验证；
- `docs/design/` 应该留给工程方案更稳定之后；
- 当前更适合作为 strategy candidate，先验证需求与 MVP 可行性。

### 待办二：HN / 社区提问验证需求

**结论：需求已有初步外部证据，但仍建议保留 Ask HN 作为社区验证动作。提问重点应聚焦“skill/rules 磁盘层维护 + gated pruning”，避免泛泛讨论 runtime context compression。**

已有证据：

- Claude Code issue #52979 反馈简单 prompt 出现 19k–31k token 开销。  
  证据：https://github.com/anthropics/claude-code/issues/52979
- Claude Code issue #33464 反馈 `CLAUDE.md`、rules files、project instructions 会在 session 启动时进入 context，power users 的 instruction 文件可能增长到 10k–15k+ tokens，整体启动上下文可能达到 20k–30k tokens。  
  证据：https://github.com/anthropics/claude-code/issues/33464
- Claude Code issue #44536 反馈 `CLAUDE.md`、memory、MCP servers、skills、rules、tool definitions 等会形成启动上下文负担，并提出 lazy context loading 需求。  
  证据：https://github.com/anthropics/claude-code/issues/44536
- 运行时 context compression 已有 Cozempic、rolling-context、context-mode 等项目，说明 token/context bloat 是真实痛点，但也说明 runtime compression 已经有较多方向在做。  
  证据：https://github.com/Ruya-AI/cozempic  
  证据：https://github.com/NodeNestor/claude-rolling-context  
  证据：https://github.com/mksglu/context-mode

社区提问重点应从：

```text
Do you need context compression?
```

改成：

```text
How do you maintain disk-level CLAUDE.md / AGENTS.md / skills / rules, and would you trust a tool that proposes deletions only after showing before/after evidence on your own tasks?
```

### 待办三：名字冲突与命名策略

**结论：不要把项目主名叫 AutoHarness。建议使用 SkillPatch Gate / SkillSlim Gate / Harness Pruner 这类更窄的名字。**

依据如下：

- aiming-lab/AutoHarness 已经定位为 Automated Harness Engineering for AI Agents，主打 governance、context management、tool governance、cost control、observability 等。  
  证据：https://github.com/aiming-lab/AutoHarness
- kayba-ai/autoharness 已经是一个 agent harness optimization control plane，会提出或应用 prompt、config、middleware、source changes，运行 evals，并根据 benchmark results 保留或丢弃候选。  
  证据：https://github.com/kayba-ai/autoharness
- neosigmaai/auto-harness 已经主打 self-improving agentic system，自动 mine failures、optimize agent harness、gate against regressions。  
  证据：https://github.com/neosigmaai/auto-harness
- AutoHarness 原论文也已经占用了“自动合成 code harness 改善 agent”的名称和叙事。  
  证据：https://arxiv.org/abs/2603.03329

推荐命名：

1. **SkillPatch Gate** — 最贴合“生成 skill/rules patch + 验证门”。
2. **SkillSlim Gate** — 更强调瘦身和验证。
3. **Harness Pruner** — 更偏 harness 维护，但可能和 pruning/context compression 混淆。
4. **RuleGate for Agents** — 强调规则执行验证，适合作为子模块名。

宣传第一句应避免：

```text
AutoHarness: self-improving agent harness optimizer
```

建议改成：

```text
SkillPatch Gate: prune and patch your coding-agent skills with evidence from your own sessions.
```

---

## 11. 社区提问草稿

> **Ask HN: How do you prune your Claude Code / Codex skills without making the agent worse?**
>
> I keep seeing the same pattern with coding agents: `CLAUDE.md`, `AGENTS.md`, `.claude/rules/`, skills, hooks, and memory keep growing over time. At some point, the agent starts every task with a large instruction footprint, but I no longer know which parts are still helping and which parts are dead weight.
>
> There are already good tools for trimming the runtime session/context window. What I have not found is a lightweight way to maintain the *disk-level symbolic layer*: skills, rules, CLAUDE.md / AGENTS.md, and memory-derived instructions.
>
> The thing I would want is not an auto-rewriter. It would build a small replay set from my own past sessions, especially tasks where I corrected the agent, then ask: if we keep, delete, compress, or rewrite this skill/rule, does it net-improve on my own history? If yes, show me a reviewable diff. If not, reject it.
>
> Questions:
>
> 1. Do you feel skill/rule/CLAUDE.md bloat in practice, or is progressive disclosure enough?
> 2. How do you decide which skills or rules to delete today?
> 3. Do you measure whether a rule is actually followed, or just assume it works?
> 4. Would you trust a tool that proposes deletions only if it shows before/after evidence on your own past tasks?
>
> Not selling anything; trying to validate whether “skill/rules maintenance with a gate” is a real pain or just a niche workflow problem.

---

## 12. 证据复核说明

本文件中涉及外部事实的核心判断已按以下来源复核：

- Claude Code token/context bloat：GitHub issue #52979、#33464、#44536。
- Claude Code 加载 `CLAUDE.md`、skills、memory、rules 等行为：Claude Code 官方 memory 与 `.claude` directory 文档。
- `AGENTS.md` / `CLAUDE.md` 配置 smell：arXiv 2606.15828。
- skill 作为外部可训练文本状态：Microsoft SkillOpt GitHub 与论文。
- coding agent eval 基础设施：promptfoo coding-agent eval 与 agent skills test 文档。
- AGENTS.md 生态：agents.md 官网与相关格式整理资料。
- AutoHarness 命名冲突：aiming-lab/AutoHarness、kayba-ai/autoharness、neosigmaai/auto-harness、AutoHarness 论文。

仍需进一步验证的部分：

- HN / 社区对“磁盘层 skill/rules 维护”的真实需求强度；
- 第一版 evidence-only report 是否能稳定抽取规则执行证据；
- replay gate 的成本、速度和可信度；
- 自动瘦身是否会引入负迁移或过度删除。
