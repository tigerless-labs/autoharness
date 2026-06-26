# design — ④ 装配（设计草稿 + provenance）

把永久笔记织成设计，每个设计元素经相对链接连起 provenance：**设计元素 → [ideas/](../ideas/index.md) → 来源卡**。设计分两类文件：脊柱一篇（原则+流水线+全局不变量+架构图）+ 每步/模块各一篇（行为边界+接口契约+验收）。过渡期此处为将来唯一设计家；现有 `docs/design/` 冻结为 legacy，以此处为准。方法由 `research-loom` skill 承载。

- 🦴 **[spine — autoharness workflow v0](spine.md)** — 系统架构图：宿主 + 学习管道（CAP→REF→校验·存储）+ 原生 skill 正常召回闭环 + 生命周期分支（MNG）+ 账本（LED）；含组件职责 / 决策 / 待解。
- 🧱 **[architecture — 代码结构 / 文件树](architecture.md)** — 最终形态 = 单个 Claude Code plugin：代码只一份（plugin）、执行只在 hook 全局层、只有数据分 global/repo、config 单点、维护逻辑 write-once；含模块落位表。

per-module 设计文档：

- **[cap](cap.md)** — CAP 捕获（哑管 + 脱敏出口 + 触发）：零内容拷贝、按指针引宿主 log；脱敏钉 egress；触发 = `Stop` + 递归 guard + 计数闸 + `SessionEnd` flush；per-session 计数器（repo-scope，与 LED per-符号 watermark 分开）。
- **[ref](ref.md)** — REF 反思（compare-first）：episode 切片 + 确定性 digest + watermark；读描述索引→定改/建/删→经 stage_skill 发 **intent**（body|delta + reason/evidence，不落盘），不产雏形。
- **[validate-store](validate-store.md)** — 校验·存储（确定性 promoter，**admission 模型**）：读 intent → 内存成型（patch=live+delta）→ 内存校验（确定性 linter、不调 LLM：skills_guard + #416 + LED 有 + 内容完整 + global repo-agnostic）→ pass：temp + `os.replace` 原子 rename + created_by + append LED；**validate-before-ANY-write、无 staging tree / 无 git**；去重靠 REF compare-first + MNG。仿 K8s admission + atomic-write。
- **[reflector-subagent](reflector-subagent.md)** — REF 的运行载体：`claude -p --agent` 跑注册子代理；**读用内建 Read/Grep/Glob、改动只走 stage_skill（发 intent、不碰 skill 树）**；写范围 = stage_skill 结构性 + path-guard backstop；detached 触发 + child-session 递归 guard。
- **[stage-skill](stage-skill.md)** — reflector 的提案工具（emit-intent）：subagent-scoped MCP，**只发 intent（body|delta + reason/evidence）、append 队列、不碰 skill 树**；复用 Hermes 校验函数（入参反馈 + promoter 防御纵深）；create 报 `level` / update promoter 解析层；**tool 前置结构、promoter 兜成型 + 内容 + 安全 + 落盘**。
- **[mng](mng.md)** — MNG 生命周期（调用率定生死 + 缓刑护新 + 容量竞争）：按 provenance 两层各圈成员；判据 = 调用率（被调次数 / 创建以来 API 请求数，repo 本层 / global 全局；分子 `PreToolUse(Skill)` handler 计、分母按每回合请求计）而非墙钟；缓刑保护新符号（样本未达成熟阈值不淘汰、不占上限），成熟池超上限按率竞争归档最低者；状态 probation→active→archived（archived 移目录出召回）；MNG handler（`PreToolUse(Skill)` + `SessionStart`）挂 plugin 单一 dispatcher、不另起注册，零 daemon；遵守度留后。

> 仍待补：LED 的 per-module 文档。`STO` 苗圃生死与 `RPL` 降级待开 [decisions/](../decisions/index.md)。
