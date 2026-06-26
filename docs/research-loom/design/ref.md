---
id: ref
type: design
---
# 模块设计：REF 反思（compare-first）

spine 的 REF 格。把一个 episode 的痕迹蒸馏成**对齐现有库的改动**。核心取向：**compare-first**——先看现有 skill、再决定改 / 并 / 新建 / 删，**直接产出终态改动**，不产真空"雏形"。运行载体见 [reflector-subagent](reflector-subagent.md)；下游交接见 [validate-store](validate-store.md)。

## 输入构造（喂什么、喂多少）

- **注入 = 最近 ~10 轮对话（exchange，config 可调），不是完整 context**。autoharness 是外挂层、拿不到宿主请求的逐字节前缀，replay 必冷——故不背全量、不照搬 Hermes 的"全量 + 暖缓存"，只喂最近这一窗。
- **喂窗下界由 CAP 的会话计数封**：触发节奏 == 喂窗大小（见 [cap](cap.md)），每满即触发 / 清零 / 喂 tail-N，故窗口只覆盖上次触发后的新 exchange、**prior episode 天然不再喂**，去重只剩"新教训 vs 现有库"一次。（[LED](validate-store.md) 另记 per-符号 watermark 作 provenance，与此触发计数**不同物**。）
- **更早的上下文默认不喂**；真遇到跨 episode 的教训才按需带——确定性截断的 digest（每条切前若干字 + 工具名，**不调 LLM**，仿 Hermes `_digest_history`），opt-in / 留后。
- 痕迹保真口取**对话回合**（用户输入 + agent 输出），非只 tool I/O；入口先过脱敏红线。

## compare-first 比对（为什么不产雏形）

先生成完整草稿再比对是反的：会在真空里造出**形状错**的 skill（本该并进 umbrella 却造了独立条目），再扔掉重做。比对必须**前置且与生成融合**：

1. 读现有 skill 的**描述索引**（便宜、就是注入上下文那份 name+desc；**取 global + project 两层并集**——create 必须两层都无才算新建，否则冷启动会重造另一层已有的）→ 锁定可能重叠的少数候选；
2. 只对候选做按需细看 → 判定 **改 X / 并进 umbrella / 新建 Y / 删**；
3. **直接产出对齐后的终态改动**：对 X 的 patch，或新 skill 的完整体，或退役决策。

语义"改>建"由模型在此完成（要读、要判断）。**dedup 是 LLM 判断，v1 只在 REF 这一处**：compare-first 定改>建即去重主防，残余交 MNG 动态兜底；**v1 不设上线前独立 inspector**（跨 skill 重复 / 漏更新的第二意见 = author≠inspector，留 [validate-store](validate-store.md) 待解），确定性侧也不搭 hash / 相似度引擎。随 N 增长靠描述索引 + 渐进披露不爆——"描述卫生"是 compare-first 的前提（[skill-recall-low-degrades-with-n](../ideas/skill-recall-low-degrades-with-n.md)）。

## 输出（交接契约）

REF **不写任何 skill 树、不碰 live、不写 staging**——它经 [stage_skill](stage-skill.md) 把每个改动**发成 intent**，交给 [validate-store](validate-store.md) 的 promoter：

- **intent** = **修改内容 + 元数据**：create / overwrite 带**完整 body**、patch 带 **delta**（`old_string→new_string`）、delete 无内容；元数据 `{name, reason, evidence}`，create 多带 `level`。
- **动作 / 层不另声明**：动作由 promoter 的存在性检查现算、层由 promoter 按两层定位解析（create 的 `level` 是唯一例外，由 REF 在 intent 声明）。
- **LED 随 intent 自带**：`reason / evidence` 是 stage_skill 必填参 → intent 必带 LED；promoter pass 才 append 进真 LED、reject 丢。

成型最终全文、读 live、内存校验、原子落盘——**全是 promoter 的事**（见 [validate-store](validate-store.md)）。跨进程交接走**文件系统**：intent append 进 per-run 队列（reflector 是 spawn 出的独立进程，唯一可靠通道是磁盘）。

## 放哪层（global / project，仅 create 决策）

宿主有两层 skill 树：**project**（限本仓）与 **global**（跨项目）。放哪由 REF 在 create 时判，轴是**「这教训关于本 repo，还是关于用户 / 通用技术」**：repo 特定（代码 / 路径 / 栈 / 约定）→ project；用户偏好（风格 / 语气 / 工作流）或通用技术 → global；拿不准 → **project（保守默认）**。**global 爆炸半径 = 每个项目都加载，故门槛高**，repo-agnostic 兜底闸在 [validate-store](validate-store.md)。

update / delete **不决策**：目标层由 promoter 按两层并集定位现有 skill 解析（在哪层就改哪层），原地写回——故 `level` 仅 create 在 intent 声明。

## 决策

- compare-first、不产雏形（省一次生成 + 避免错形状）。
- episode 切片 + 确定性 digest + watermark（外挂无暖缓存 → 喂得少才省；旧内容不重看）。
- 反思的产物只是 **intent**（不落盘），由确定性 promoter 成型 / 校验 / 落盘定生死（见 [validate-store](validate-store.md)）。
- **LED 随 intent 自带**（`reason / evidence` 是 stage_skill 必填参）；promoter pass 才 append、reject 丢——产出 ≠ 入账。
- **放哪层仅 create 决策**：repo 特定 → project、用户偏好 / 通用 → global、默认 project、global 严；update / delete 的层由 promoter 解析。

## 待解

- **episode 边界信号**：turn 结束 / 任务完成 / token 预算 —— 未定。
- 跨 episode 的教训（一条 lesson 横跨多个 episode）：watermark 切片下如何不丢——按需带前几轮，机制待定。

provenance：[episode-boundary-reflection](../ideas/episode-boundary-reflection.md)（粒度 / 时机 / digest）、[trace-based-pattern-extraction](../ideas/trace-based-pattern-extraction.md)（捕获口）、[skill-recall-low-degrades-with-n](../ideas/skill-recall-low-degrades-with-n.md)（描述索引使 compare-first scale）；compare-first 偏好序与 digest 源出 [Hermes](../sources/github/nousresearch-hermes-agent.md)。
