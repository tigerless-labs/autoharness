---
id: reflector-subagent
type: design
---
# 模块设计：reflector 子代理（REF 的运行载体）

[REF](ref.md) 这步**不在主会话里跑**，由一个注册的 Claude Code **subagent** + **hook spawn** 承载。本文定它的定义、**文件编辑范围限制**、触发与递归 guard。

## 为什么 subagent + spawn

- 我们是外挂层、不占宿主 agent loop，**只能 spawn**。`claude -p --agent <name>` 直接**以该 subagent 身份**跑：subagent 的正文**整个替换**默认 system prompt（同 `--system-prompt`），带它的工具限制 + 模型，**无主 agent 那一跳**。
- subagent 是**可版本化的一等产物**（随 plugin 作 `<plugin>/agents/` 组件分发，见 [architecture](architecture.md)）——干净、native、装一次到位。
- 对比裸 `claude -p "<prompt>"`：subagent 把 review/authoring 提示 + 工具限制 + 模型**注册一次**，比每次拼 flag 干净；也比让主模型在 turn 内调 Agent 工具更可控（那是概率触发、且在关键路径上）。

## 定义要点

- **便宜模型**（如 haiku）：reflection 不需主模型。
- **最小权限工具**：**读**用内建 `Read` / `Grep` / `Glob`（`Read` 读已知路径、`Grep` 搜内容、`Glob` 枚举两层 skill 树 / 候选 `references/`——compare-first 细看现有 skill 用；episode 与描述索引靠注入、不靠工具取）；**改动**只走自产的 **[stage_skill](stage-skill.md)**（发 intent、append per-run 队列、**不碰任何 skill 树**），**去掉通用 Write/Edit**，**不给 Bash / 网络**。subagent 默认继承宿主全部工具，故必须**显式收窄**（deny-by-default、least privilege，[additive-over-native-skill](../ideas/additive-over-native-skill.md)）。执行类（跑命令验证）留到 dry-run 阶段再按需加。
- **正文** = compare-first 的 review + authoring 提示（仿 Hermes `_SKILL_REVIEW_PROMPT`；compare-first 偏好序见 [ref](ref.md)）。**格式与创建要求 = 一份单独维护的权威 spec**（必填 frontmatter / 命名 / 结构 / references 约定 / 放哪层 / 不可捕获项），**不靠"读现有 skill 当样例"推断**——冷启动可能没有、现有（含 native）格式可能不合本 spec。这份 spec **同时喂 REF（按它写）与 [validate-store](validate-store.md) 的 #416 linter（按它验）**，是同一契约的两面、单一来源（config 一类）、保持同步——但**它不静态嵌进本 agent 正文**（那会成第二份拷贝、与 linter 漂移），而是由 spawn 在拼装时**运行时注入** reflector 输入（见下「spawn 拼装」）。现有 skill 只供 compare-first（去重 / 放哪层），**不当格式源**。

## spawn 拼装与交接

主会话 hook 在 episode 边界触发后，由 spawn 步（`hook/spawn.py`）**确定性**拼装 reflector 的输入，跨进程经磁盘交接（reflector 是独立子会话、碰不到主会话内存）：

- **三件套**：CAP 物化的脱敏 episode 窗（[cap](cap.md) 的交接物）+ 现有两层 live skill 的**描述索引**（每符号 `name`+`description`，compare-first 去重 / 放哪层的唯一依据，跳归档）+ 单一来源 `format_spec`（authoring 契约，与 #416 linter 同源）。三者**靠注入、不靠工具取**，故 reflector 的读工具只用于 compare-first 细看候选正文。
- **身份注入**：spawn 置递归 guard 信号（`CLAUDE_CODE_CHILD_SESSION`）+ 把本 run 的 intent 队列坐标（run_id / repo 根）经**环境**传给子会话，[stage_skill](stage-skill.md) 据此 append 回正确队列。
- **接力**：spawn 出的子会话以 reflector 身份跑完（只可能 append intent），spawn 返回后接 [validate-store](validate-store.md) 的 promoter——读队列、校验、原子落盘。author 与 land 自此彻底分进程。

## 文件编辑范围限制（钉死写范围）

reflector **不写任何 skill 树**，禁碰 live（两层 `~/.claude/skills` + `./.claude/skills`）与非自产符号。纵深：

1. **主（结构）**：reflector **没有通用 Write/Edit**，唯一写工具 [stage_skill](stage-skill.md) **只 append intent 队列、不碰 skill 树**——"动到 live / 用户 skill"在此**结构上不可能**；连 staging 文件都不写（成型 / 落盘全在 promoter）。
2. **backstop（防御纵深）**：**plugin 顶层 `hooks/hooks.json` 的 PreToolUse hook**按 reflector 的 `agent_type` 匹配，对其 `Write`/`Edit` 调用 deny（exit 2 / stdout JSON `permissionDecision`）——防 tool 有 bug 或意外写路径。**不放 agent frontmatter**：plugin-shipped agent 的 `hooks`/`mcpServers` 字段被宿主出于安全忽略（[E6](../../../experiments/E6_platform_contracts/results.md) S1），故 backstop 退到顶层、按 `agent_type` 精确匹配（S3 确认子代理自身工具调用触发 PreToolUse 且 payload 带 `agent_type`）。把 [lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)（只动自产）+ [additive-over-native-skill](../ideas/additive-over-native-skill.md)（不碰原生 / 用户 skill）+ 安全铁律落在**写入 chokepoint**。

> 分工：reflector 只发 intent、进不了 live；live 的写由 [validate-store](validate-store.md) 的 promoter 独占（admission：内存校验 → 原子落盘），按 `created_by:agent` 收口。

## 触发与递归 guard

- **触发**：主会话 hook（episode 边界，如 Stop）在 **detached 后台作业**里 spawn reflector（仿 ECC `nohup` daemon，不堵关键路径），spawn 返回后接 [validate-store](validate-store.md) 的 promoter。
- **递归 guard**：spawn 出的子会话会再触发 hooks；用 `CLAUDE_CODE_CHILD_SESSION`（Claude Code 自设、子会话才有）在反思触发 hook 里现判——有值即 exit，防"反思套反思"。

## 平台契约（[E6](../../../experiments/E6_platform_contracts/results.md) 已闭）

- **S1**：plugin-shipped agent 的 `hooks`/`mcpServers` frontmatter 被忽略 → backstop 退顶层 `hooks.json`、stage_skill 退顶层 `.mcp.json`。
- **S3**：子代理自身工具调用触发 PreToolUse，payload 带 `agent_id`/`agent_type`；deny = exit 2（stderr）或 exit 0 + stdout JSON `permissionDecision: deny`。
- **S4**：省略 `tools` 全继承（故仍显式写最小集）；plugin agent 解析为 `plugin:reflector`；**SubagentStop 与 Stop 分立**——reflector 自身 Stop 自动转 SubagentStop，故 CAP 只数主 Stop、reflector 完成不灌计数（与 `CLAUDE_CODE_CHILD_SESSION` 递归 guard 双保险）。
- **安装位**：`agents/reflector.md` 作 plugin 内组件随装就位，**不拷进用户 `~/.claude/agents/`**。

残留留 live spike（行为质量，非平台能力）：reflector compare-first 真改优于建、最小权限不越界、backstop 运行时真 deny 一次 `Write`（归 `experiments/`、Phase 5 live）。

provenance：[additive-over-native-skill](../ideas/additive-over-native-skill.md)（零侵入 + 最小权限）、[lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)（只动自产）、[episode-boundary-reflection](../ideas/episode-boundary-reflection.md)（REF 内容）；运行形态对照 [Hermes](../sources/github/nousresearch-hermes-agent.md)（进程内 fork）、[ECC](../sources/github/affaan-m-ecc.md)（spawn `claude -p` haiku 自写 + daemon 触发）。
