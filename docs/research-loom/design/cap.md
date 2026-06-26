---
id: cap
type: design
---
# 模块设计：CAP 捕获（哑管 + 脱敏出口 + 触发）

spine 的 CAP 格，**学习管道经 hook 观察的捕获入口**（MNG 的计数 / curation handler 另挂同一 dispatcher，非另起注册）。它不采集内容、不裁决，只做三件事：把宿主 log 当采集源**按指针引用**、在 egress 过**脱敏红线**、在 episode 边界**触发 REF**。裁决（抽模式 / 去重 / 改建删）全是 [ref](ref.md) 的。

## 不自存：宿主 log 即采集源

宿主（Claude Code）本就把整段 transcript（用户输入 + agent 输出 + tool I/O）落 session log，hook 入参直接给 `transcript_path`。CAP 再抄一份内容即重复（违反单一权威源 / DRY），故 **CAP 零内容拷贝**：只维护「指针 + 计数」的薄索引，喂 REF 的近窗在触发那刻从宿主 log 现算（`tail` 最近 N exchange）。tool I/O 已在 transcript 里，无需另设 `Pre/PostToolUse` hook。

> host-agnostic 的真义：transcript 格式与 hook 名都是 Claude Code 特有，"host-agnostic" 指**跨项目 / 跨仓**通用，非跨 agent 框架。CAP 内部绑宿主 hook + log，对外只暴露「给我近 N exchange 窗口」一条契约。

## 脱敏红线在 egress（不在入口存储）

读用户原话使 PII / 密钥概率远高于只读 tool I/O（[trace-based-pattern-extraction](../ideas/trace-based-pattern-extraction.md)），故脱敏是硬要求。但 CAP 不自存 —— 红线因此钉在 **CAP 的出口**，非某份存储副本：宿主 raw log 保持 raw（不是我们的、不碰），凡**从 CAP 越界往外**的东西（喂 REF 的近窗切片、写进 [LED](validate-store.md) 的证据切片 / 指针）一律过红线。脱敏发生在「物化给下游那一刻」。红线规则集（secret-scan + PII）是 CAP 与 LED 共用的**单一来源**（config 一类，待建）。

## 触发：Stop hook + 计数闸

唯一能拿到「每次响应结束」的信号是 **`Stop` hook**。但 Stop = 每轮、episode = 一个跨多轮的任务，故不每个 Stop 都 spawn。触发逻辑全程确定性、不调 LLM：

1. `CLAUDE_CODE_CHILD_SESSION` 有值 → 早退（递归 guard：reflector 自己的 Stop 不得再触发反思，并阻止计数）。
2. 计数器 +1；未满 `reflect_every_n`（config，默认 10）→ 退出。
3. 满 → detached 后台作业里 spawn reflector（不堵主 loop），计数器清零。

**`SessionEnd` flush**：会话结束时计数 > 0 即把余量反思掉，否则不满阈值的尾巴永远丢；当前计数值正好告诉 REF 喂几个。spawn 机制 / 递归 guard 的载体见 [reflector-subagent](reflector-subagent.md)，本步只定**何时**触发与**交什么**。

**交接物 = 脱敏后物化的 tail-N 窗口**：触发那刻 CAP 从宿主 log 取最近 N exchange（N = `reflect_every_n`，故「每 N 轮触发」与「喂最近 N 轮」是同一个数、对齐零重叠）、过 egress 红线、把脱敏后的窗口物化给 reflector 读（reflector 是 spawn 的独立进程，跨进程走磁盘），用完即弃。REF 拿到的从不是 raw transcript。

语义上的「任务真做完」边界（task-done / token 预算）未定，v0 以「攒够 N」近似；切多切少不致命 —— compare-first + 下一窗兜底。

## 计数：per-session 计数器

**触发节奏 == 喂窗大小**（同为 `reflect_every_n`）：每满即触发、清零、REF 喂 tail-N，两边界重合 → 零重叠，无需另设 watermark 封下界。计数器本身即边界。

**每个 Stop = +1，不扫 transcript**：Stop 一轮 fire 一次，hook 触发本身即增量 —— 读小 int → +1 → 写 → 比 N，O(1)。不从 transcript 长度现算：`.jsonl` 行数要扫整文件（越扫越大）且 tool 行灌水（行数 ≠ 轮数），那个小 int 文件本身就是 O(1) 的「现成轮数」。transcript 只在触发那刻读一次（取 tail-N 窗口），非每轮。

- **session 级、一 session 一个**：计数单位就是 session-id —— transcript 一 session 一份，跨 session 共用无意义。repo 不是第二根轴；一 session 只属一 repo，文件落该仓 `.claude/` 只是「住在哪」，非「按 repo 聚合」。
- **落盘位置**：repo 的 `.claude/` 内 CAP 自有 state 区（git-ignored、纯叠加），**绝不入 live `.claude/skills` 或 staging**。每个 Stop 是独立进程，整数必落盘（进程内存留不住）。
- **生死随 session**：`SessionEnd` flush 后自删；崩溃 session 的孤儿惰性 GC（`SessionStart` 扫，留待解）。

**与 LED 的 per-符号 watermark 拆分**：CAP 这个是「会归零的会话计数器」，管触发 + 喂窗；[LED](validate-store.md) 那个是 per-符号 provenance（已反思到哪），Commit 那刻记。二者零重叠 —— 一个没产出任何符号的 session 也得有 CAP 计数（否则空转重反思），故不能并进 LED。

## 决策

- 零内容拷贝、按指针引宿主 log（避免重复存储、守单一权威源）。
- 脱敏钉 egress、非入口存储（"不自存" 与 "入口脱敏" 的唯一自洽解）。
- 触发 = `Stop` + 递归 guard + 计数闸 + `SessionEnd` flush，全确定性、不调 LLM。
- 触发节奏 == 喂窗大小 → 计数器一物双用，消掉独立 watermark。
- 计数 session 级、落盘于 repo 内 CAP state 区（不入 live / staging）；与 LED 的 per-符号 watermark 分开。

## 待解

- **episode 边界信号**：task-done / token 预算 —— 未定（与 [ref](ref.md) 共享），v0 用计数近似。
- **session-id → transcript 路径**的发现：实测确认 hook 入参足够定位；并确认 compaction 下 tail-N 取到的仍是原始轮次（而非已压缩摘要），否则喂窗保真受损。（计数不依赖 transcript 长度，故 compaction 不影响计数，只影响取窗。）
- **触发到读取的 race**：满 N 到 detached reflector 真读 transcript 之间又来 1~2 轮，`tail-N` 漏最老 1~2；v0 容忍，精确化留 spawn 时带 transcript 上界。

provenance：[trace-based-pattern-extraction](../ideas/trace-based-pattern-extraction.md)（捕获口取对话回合 + 脱敏更硬）、[additive-over-native-skill](../ideas/additive-over-native-skill.md)（零侵入：只经 hook、不碰原生加载链）；触发载体见 [reflector-subagent](reflector-subagent.md)，触发形态对照 [ECC](../sources/github/affaan-m-ecc.md)（`Pre/PostToolUse` 抓 + `nohup` daemon 触发）。
