---
id: validate-store
type: design
---
# 模块设计：校验·存储（确定性 promoter，admission 模型）

spine 的 校验·存储 格。它是宿主 skill 树的**唯一确定性写者**：读 reflector 经 [stage_skill](stage-skill.md) 发来的 **intent**（提案），**内存里成型最终全文、内存里校验，过了才原子落盘**。模型只 propose、碰不到盘——land 与校验全在这。仿 **K8s validating admission**（校验 in-flight 对象、allow 才 persist）+ **POSIX atomic-write**（temp 同目录 + 原子 rename）。

## validate-before-ANY-write（admission 模型，强于 Hermes write-first）

Hermes `skill_manage` 是 **write-first**：先 `_atomic_write_text` 落盘、再（默认 no-op）扫描、出事回写——坏内容先碰盘。我们反过来、且更彻底：**校验通过前任何盘都不落**。

```
reflector ──stage_skill──► intent（不落盘）
   promoter：
     ① 成型最终全文（内存）：create/overwrite=full body；patch=读 live+应用 delta；delete=标记移除
     ② 校验（内存）：linter 六类（见下），此刻同握 old=live + new=成型结果
     ③ pass → hardcode 盖 `created_by`（create 对象）→ 写 temp（live 同目录 `.SKILL.md.tmp`）+ fsync + os.replace 原子改名 + sidecar（含标签）→ live
        reject → 什么都没写、不打标
```

- **谁读 live**：promoter，**且只在 patch**（应用 delta 必须有 base）；create / overwrite / delete 不读。**没有"先把 live 抓进暂存区再改"这一步**——它本不该存在。
- **唯一落盘 = pass 后的 temp + 原子 rename**：temp 必须同目录才能原子改名，且 `.tmp` 不是 `SKILL.md`、live-detect 忽略。原子 = live 永不半态。
- 旧不变量 validate-before-**live**-write 升级为 validate-before-**ANY**-write：连暂存那次盘也不落。

## 没有 staging tree

整棵镜像 skill 树（per-run 子目录 / 逐 skill 拷贝 / 清理 / 孤儿）**不存在**。要清的只剩两样、都轻：

- **per-run intent 文件**（stage_skill append 的小队列）：promoter 处理完即删。
- **孤儿 `.SKILL.md.tmp`**：只在"写 temp 与 rename 之间崩溃"才留，启动按前缀 sweep（atomic-write 卫生）。

## Validate（一道确定性 linter，跑在内存成型结果上，不调 LLM）

逐 intent 跑，产 verdict `{pass / reject + findings}`，**全确定性**（快、精确、不可注入）。查六类：

- **安全**：`skills_guard`（见下）。
- **结构（#416）**：frontmatter 可解析 + 必填（name / description）；引用的**文件存在**；`.py` 过语法解析；无断 symlink。
- **LED 有没有**：intent 必带 LED（`reason / evidence` 是 stage_skill 必填参），缺 / 空即 reject——每次 land 都在账上有据。
- **内容完整**：无 `TODO` / 占位符 / 空节。
- **global 更严（repo-agnostic）**：`level=global` 含 **repo-local 标识**（绝对路径 / 本仓名 / repo 专有 id）→ 降 project 或 reject。global 爆炸半径 = 每项目都加载，从严；project 不设。
- **自产标签（只动自产）**：`update / patch / delete` 的目标 live skill **必带 `created_by:agent`**（hardcode 读 sidecar），无标签即 reject——不碰用户 / 原生 / 外来 skill（[additive-over-native-skill](../ideas/additive-over-native-skill.md) / [lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)）。`create` 无目标、豁免此**查**；它的**打标**不在校验里——而在**六类全 pass 之后**才 hardcode 盖（写随 land，见下），**未过校验绝不打标**。

action（create / update）由"live 对应物在不在"现算（存在性检查），**不设撞名检查**；`level`：create 在 intent 声明、update / delete 由 promoter 按两层定位现有 skill 解析；`delete` 由 intent 显式。

**去重不在这道闸**：靠 REF compare-first（作者读描述索引定改>建）+ MNG 动态兜底，**不设上线前独立判断**（见[待解](#待解)），确定性侧也**不搭** hash / 相似度引擎。

## Commit / 原子发布（pass 才发生）

- **create / update** → （**pass 后**）hardcode 盖 `created_by:agent`（create）→ 写 temp 同目录 + `os.replace` 原子 rename 进**对应层**（create → intent 的 `level`；update → 定位到的 live 层）+ sidecar（含标签，随 land 原子写）+ 把 **intent 自带的 LED 条目** append 进真 LED（append-only、只记既成事实）。**查在校验内、盖在 pass 后、写在 land——reject 绝不打标。**
- **delete** → 原子移除 + 交 MNG 归档 + LED 退役事件。
- **reject** → 什么都没写、不入账（watermark 已防重复反思，不为"拒绝留痕"另立机制）。
- **并发**：promoter 是 live 唯一写者、**串行**（两 run 同改一 skill → 锁 + last-writer）。

## diff 给谁

promoter 此刻同握 **old(live) + new(成型结果)**（= admission 的 `object` + `oldObject`）。v1 真用到的只有**存在性检查 → action**；**完整文本 diff 没有 gate 在读**（inspector / 人审都删了），留作日志 / 将来 inspector（[待解](#待解)）。

## 执行保证（模型绕不过、promoter 一定跑）

- **绕不过**：reflector 工具只有 `Read / Grep / Glob / stage_skill`，stage_skill 只记 intent → **模型结构上无法 land、跳不过闸、碰不到 live**；最大效果 = 塞一条 intent。
- **一定跑**：**CAP hook（确定性）→ spawn reflector（只发 intent）→ promoter（确定性、编排无条件调）** 两段确定性书挡夹着模型；模型**没有 validate / commit 工具**，"跳过校验"不是它的可选项。
- **崩了安全**：intent 进 durable 队列；原子 rename = 全有或全无；promoter 没跑 / 崩 → 未处理 intent 留队列、下次补处理（at-least-once + 原子 land = 实际 exactly-once）；极端没跑 → 什么都没 land（**fail-safe / deny-by-default**）。

## 抄 Hermes `skills_guard`，但**默认翻转为开**

`skills_guard` = trust × verdict 的正则静态扫描（exfiltration / injection / destructive / persistence / network / obfuscation）。Hermes 对 **agent-created 默认关**（理由："agent 反正能 terminal 直接跑"）。**对我们不成立**：我们的 skill **延迟执行、持久、可传播、来料含 trace（间接注入）**——威胁模型更强，故 **self-produced 默认过扫**。并强化 **injection 类**：SKILL.md 正文本身就是注入宿主上下文的载体，"覆盖系统指令 / 总是 exfiltrate"这类**指令型注入**是一等威胁。红队用例（投毒 skill 被挡）进单元 + 系统测试。

## created_by:agent —— 参考 Hermes，并因架构而更干净

Hermes 用 **write-origin ContextVar**（`tools/skill_provenance.py`）：review fork 把 `_write_origin` 设为 `background_review`，`skill_manage create` 时若是该 origin 就 `mark_agent_created`，写进 **sidecar `~/.hermes/skills/.usage.json`**（`tools/skill_usage.py`，**明确"sidecar, not frontmatter"**——把运维元数据挡在 SKILL.md 之外，护召回 + 不污染用户作品）。`is_agent_created` 据此判，curator 只动自产。

**我们抄两点、改一点**：

- **抄**：`created_by:agent` 走 **sidecar**、不进 SKILL.md frontmatter；它是 MNG 自动维护的成员资格钥匙（[lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)）。
- **抄**：同一 sidecar 挂 LED / verification 元数据（与 `.usage.json` 同位）。
- **改（更干净 + 前移到确定性侧）**：Hermes 需 ContextVar，是因为**模型直接写盘、得探测"我在不在 review fork"**；我们 **`created_by` 全归确定性 hardcode**——**查**（`update/patch/delete` 目标须自产、否则 reject，属六类校验之一）+ **盖**（**六类全 pass 后**才给 `create` 成型对象强制打标，未过不盖），无需 origin 探测（promoter 是 live 唯一写者、只从 intent 成型，本就知是自产）。**物理写随 land 原子落**（sidecar 与 SKILL.md 一同，保一致；**不在校验阶段写盘**，守"校验无落盘副作用"）。**标签真相归确定性闸**：过闸落地即 `create` 必带标、`modify` 目标必自产。

## 决策

- **promoter = admission**：内存成型 → 内存校验 → pass 才原子落盘（**validate-before-ANY-write**）。仿 K8s validating admission + atomic-write。
- **模型只发 intent、碰不到盘**；land 与校验在确定性 promoter，模型**无工具可跳**——执行保证靠"确定性书挡 + 能力受限 + durable 队列 + fail-safe"。
- **唯一落盘 = temp 同目录 + `os.replace` 原子 rename**；live 永不半态；**无 staging tree、无版本史**。
- **谁读 live = promoter 且只 patch 时**（应用 delta 需 base）；create / overwrite / delete 不读。
- **linter 六类**（安全 `skills_guard` + #416 结构 + LED 有 + 内容完整 + global repo-agnostic + **自产标签**），跑在内存成型结果上，**全确定性、不调 LLM**。
- **去重不在闸**：REF compare-first + MNG 动态；合理性靠随用随验（[dynamic-validation-lifecycle](../ideas/dynamic-validation-lifecycle.md)）。
- **format 单一来源契约**：必填 / 结构 / references 约定 = 单独维护的 spec，**authoring（reflector 正文）与 #416 linter 同源**。
- **action 存在性现算**（不设撞名）；**`level`**：create 在 intent 声明、update / delete promoter 解析；`delete` 由 intent 显式。
- **LED 在 intent 自带**（stage_skill 必填 `reason / evidence`），pass 才 append 真 LED（append-only），reject 不入账。
- created_by 走 sidecar；**确定性 hardcode 查 / 盖**（modify 目标须自产否则 reject、属六类之一；create **过六类校验后才**打标、未过不盖），不用 origin 探测；物理写随 land 原子落、保 sidecar 与 SKILL.md 一致。
- skills_guard self-produced 默认开（威胁模型强于 Hermes）。

## 待解

- **独立判断层（跨 skill 重复 / 漏更新）**：v1 删去——去重只靠 REF compare-first + MNG。将来可加一个独立 cheap LLM（吃 diff + LED + 全库描述索引）补 REF 的库级盲点（author ≠ inspector，#25833③ 的最小实现）；fancpp 的两个确定性正则（引用 **tool** 存在 / 负向断言 #6051）是更轻的候选，可先于 LLM 收。
- **文本 diff 的消费者**：v1 无 gate 读（只用存在性→action）；留日志 / 将来 inspector。
- **intent 队列是否持久**：要崩溃补处理就留、处理完删；不要更轻（崩了 fail-safe 丢这轮学习）——取舍待定。
- **dry-run 复现性**（#25833①）：留后，需计算 sandbox。**一致性 / success_rate**（#25833②）：归 MNG，留后。
- **并发同改一 skill 的锁粒度**：待定。

provenance：[skill-recall-low-degrades-with-n](../ideas/skill-recall-low-degrades-with-n.md)（去重 / 描述卫生）、[precipitate-storage-layer](../ideas/precipitate-storage-layer.md)（`.claude/skills`）、[adherence-driven-curate](../ideas/adherence-driven-curate.md)（consolidation 改/建/删）、[record-scenarios-for-eval](../ideas/record-scenarios-for-eval.md)（LED）、[lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)（created_by 成员资格）；机制对照 [Hermes](../sources/github/nousresearch-hermes-agent.md)（write-first / skills_guard / write-origin sidecar / #416 lint / #25833 挂起）、[ECC](../sources/github/affaan-m-ecc.md)（乐观写入、无门）；新机制对照 **K8s validating admission**（校验 in-flight、allow 才 persist）+ **POSIX atomic-write**（temp 同目录 + 原子 rename）——源卡待建。
