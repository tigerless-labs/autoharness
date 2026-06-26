# roadmap — autoharness 实现执行顺序 + 测试策略

> 工作艺术品，非设计文档。装配自 [research-loom/design](../research-loom/design/index.md)，以
> [architecture](../research-loom/design/architecture.md)（代码落位）与 [spine](../research-loom/design/spine.md)（管道职责 + 全局不变量）为准。

构建顺序 = **数据依赖自底向上**：`lib/` write-once 原语是地基（人人复用），promoter 是安全闸（最先建牢），CAP/REF/MNG 各自挂上去，plugin 打包收尾。平台机制的不确定性（Claude Code 的 plugin/agent/MCP/hook 行为）**不能单测**，提前为 **Phase 0 spike**、在真宿主上验、记 `experiments/`、决定投递形态后才动相关 Phase。

**测试只住仓库根 `tests/`**，按 `tests/test_<module>.py` 镜像模块；plugin 树内不放测试、测试不随 plugin 分发（[architecture](../research-loom/design/architecture.md) 已钉）。`pytest.ini` 的 `testpaths=tests` 物理封死收集范围。

## 测试三层（每个 Phase 只引用，不重述）

| 层 | 用于 | 在哪跑 | 断言什么 |
|---|---|---|---|
| **unit** | 确定性纯函数：`lib/` 全部原语、promoter、MNG、validate、skills_guard、redact、counters、lifecycle、dispatch 路由 | `tests/test_<module>.py`，`tmp_path` fixture、不连外部服务 | **关系 / 不变量**（率序、reject 零落盘、原子 rename 无半态、分母=层计数−锚），非硬编码值；**红队用例**（投毒挡、越权 reject、注入挡） |
| **system（管道集成、无 LLM）** | CAP→spawn→promoter→sidecar/LED 全链 | `tests/`，用 **fake reflector**（吐 canned intent 的脚本替真模型）驱动，文件系统真落 `tmp_path` | 端态：该落的落、该拒的零变化、LED 既成事实入账 |
| **live host / sandbox spike** | 平台机制：plugin-agent frontmatter、MCP subagent-scope、`PreToolUse` deny 协议、`Skill` 调用捕获 + 符号身份、transcript 发现 + compaction、`--agent` 继承 | 真 Claude Code，人工 / 脚本 harness，记 `experiments/` 为 evidence | yes/no 结论 + 投递决策；**`@pytest.mark.live` 标记，CI 默认排除** |

判据：**确定性的（lib/promoter/MNG/validate/skills_guard/CAP 触发）尽量 unit + system 全覆盖**；**只有依赖活宿主的（LLM 反思质量、hook/MCP 真生效、Skill 真触发）才落 live spike**——后者不堵 CI，靠 fake reflector 把管道接缝在 CI 里测掉。

## CI（GitHub Actions，PR + push 到 main 触发）

单 workflow `.github/workflows/ci.yml`：装 pytest → 两个 doc checker（`check_doc_links` / `check_research_loom`）+ 各自 `--selftest` → `pytest -m "not live"`（live 排除、空收集容忍 exit 5）。任一红即 PR 不可合。doc checker 现已全绿、即刻可门禁；产品测试随 Phase 落地自动纳入（`testpaths=tests`）。

## Phase 0 — 平台机制 spike（gate，全 live-host，归 `experiments/`）

动相关 Phase 前必须有结论的实测，汇自各 per-module「动手前实测」：

- plugin-shipped agent 是否支持 `hooks` / `mcpServers` frontmatter（[architecture](../research-loom/design/architecture.md)）→ 决定 reflector backstop 与 stage_skill 注册退不退到 plugin 顶层。
- MCP 工具能否 scope 到单 subagent（[stage-skill](../research-loom/design/stage-skill.md)）。
- subagent 自带 `PreToolUse` hook 是否对其自身工具调用生效；deny 的确切协议（exit code vs JSON）（[reflector-subagent](../research-loom/design/reflector-subagent.md)）。
- `--agent` 省略 `tools` 是否全继承；plugin 内 `plugin:reflector` 能否被 hook spawn 解析（[reflector-subagent](../research-loom/design/reflector-subagent.md)）。
- learned skill 被用是否走 `Skill` 工具、触发 `PreToolUse(Skill)`，payload 是否带解析后符号身份（[mng](../research-loom/design/mng.md)，率分子前提）。
- session-id→transcript 发现充分；compaction 下 tail-N 取到原始轮次（[cap](../research-loom/design/cap.md)）。

**测试方法**：手点 / 脚本 harness 在真 Claude Code 上跑，每项落 `experiments/` 一条 evidence；**不进 CI**。**退出条件**：每个 spike 有 yes/no + 投递决策。

## Phase 1 — config + `lib/` write-once 原语（地基）

`config.py` 单点（节奏 / 成熟阈值 / 上限分层 / 红线集 + format_spec 指针）+ `layer` / `skill_store` / `sidecar` / `ledger` / `counters` / `redact` / `validate` / `skills_guard` / `intent_queue`。最底层、全管道复用、纯确定性。

**测试（unit）**：`layer` 由入参解析两层落盘位；`skill_store` 原子写 + 两层 `find` + 应用 delta；`sidecar` 单实现读写 created_by/计数/verification；`ledger` append-only（只增不改）；`intent_queue` append / drain / 启动 sweep 孤儿（writer=stage_skill、reader=promoter 同源一份）；`counters` 按层分子分母、O(1) 读改写；`redact` 红线消费（窗口切片 / LED 证据出口）；`validate` 六类 linter 跑在内存成型结果上；`skills_guard` 六族正则（exfiltration/injection/destructive/persistence/network/obfuscation）。**红队**：`skills_guard` 挡投毒 / 指令型注入；`redact` 不漏 PII / secret；global 含 repo-local 标识被 `validate` 降级或 reject。

## Phase 2 — promoter 校验·存储（admission 闸 + 原子落盘）★安全 chokepoint

`hook/promoter.py` 复用 Phase 1。validate-before-ANY-write、内存成型（create/overwrite=body、patch=live+delta、delete=移除）、内存校验六类、pass→hardcode 盖 `created_by`+temp 同目录+`os.replace`+sidecar+append LED、reject 零落盘、串行单写者。

**测试（unit + 文件系统集成，`tmp_path`）**，断言不变量：**reject 后盘上无任何变化**；原子 rename 后 live 永不半态；孤儿 `.SKILL.md.tmp` 启动按前缀 sweep；patch 由 `live+delta` 重建；`update/patch/delete` 目标非 `created_by:agent`→reject；缺 LED→reject；含 `TODO`/占位符→reject；global 含 repo-local→降级 / reject；create 过六类后才打标、未过不打标。**红队（最重）**：投毒 intent 被六类挡；模型结构上 land 不了（无 commit 工具面，只能塞 intent）；注入型 SKILL 正文被 `skills_guard` 挡；崩溃下 intent 留 durable 队列、下次补处理（at-least-once + 原子 land）、极端没跑则零 land（fail-safe）。

## Phase 3 — stage_skill MCP（emit-intent 提案面）

`stage_skill/server.py`：schema 强制 `{action,name,level,body|delta,reason,evidence}` 结构 + 必填 LED 字段；复用 Phase 1 校验函数给入参即时反馈；**只 append intent 队列、不碰 skill 树**。

**测试（unit）**：schema 拒残缺 / 越界 enum / `body`+`delta` 互斥违例；入参即时校验（frontmatter/size）反馈；append 后 skill 树零变化。**live spike**：MCP 只 reflector 可见、正常会话不可见（Phase 0）。

## Phase 4 — CAP 捕获 + 触发

`hook/{on_stop,on_session_end,capture}` + `counters` + `redact`。零内容拷贝指针索引、egress 脱敏、`Stop`+递归 guard+计数闸+`SessionEnd` flush、tail-N 物化喂 REF。

**测试（unit + 集成）**：计数器每 Stop +1 / 满 `reflect_every_n` 触发并清零 / 不扫 transcript；`CLAUDE_CODE_CHILD_SESSION` 有值即早退（递归 guard 且不计数）；`SessionEnd` 计数>0 才 flush 余量；egress 红线作用在物化窗口而非宿主 raw log；tail-N 窗大小 == 触发节奏（零重叠）。集成用 tmp transcript fixture 取窗 + 孤儿计数 `SessionStart` GC。**live spike**：transcript 发现 / compaction（Phase 0）。

## Phase 5 — reflector 子代理 + spawn

`agents/reflector.md`（定义、最小权限 `Read/Grep/Glob/stage_skill`、compare-first 正文 + format_spec）+ `hook/spawn.py`（确定性拼装 episode 窗+描述索引+format_spec → detached spawn → 接 promoter）。

**测试**：spawn 输入拼装 **unit**（三件套注入正确、跨进程走磁盘）；**system**：**fake reflector**（脚本吐 canned intent）驱动 CAP→spawn→promoter 全链、`tmp_path` 真落盘，assert 终态符号 + sidecar + LED。**live spike**：reflector 正文行为（compare-first 改>建、最小权限不越界）、`PreToolUse` backstop 真 deny Write（Phase 0）。

## Phase 6 — MNG 生命周期

`hook/{on_session_start,on_skill_call}` + `lifecycle` + `counters` + `sidecar`。调用率定生死、缓刑护新、容量竞争、惰性 `SessionStart` 现算、archived 移目录出召回。

**测试（unit + 集成）**：`rate=分子/分母` 按层（repo 本层 / global 全局）；缓刑（分母未过成熟阈值）不淘汰、不占上限；毕业即审、率≈0 当场归档；成熟池超上限按率升序归档最低者；archived 移出 live 树、移回复活（可逆）；判定只读 sidecar+层计数器累积水位 → 任意 repo 的 `SessionStart` 同一结论。集成：`PreToolUse(Skill)` 分子 +1、每回合分母 +1、promote/archive 的 `mv` 原子带走分子。**live spike**：Skill 真触发 + 符号身份对齐（Phase 0）。

## Phase 7 — plugin 打包 + 单 dispatcher + marketplace + 端到端

`.claude-plugin/plugin.json`、`hooks/hooks.json`→`dispatch` 单入口、`.mcp.json`、`agents/reflector.md` 就位；自建 marketplace repo（含 `marketplace.json`）。首次运行两层数据区惰性建。

**测试**：`dispatch` 路由 **unit**（事件名→正确 `on_*`、未知事件安全忽略）；**端到端 system**：真 Claude Code 装 plugin、跑一会话、确认符号落 `.claude/skills` 经原生 description 召回、archived 不再注入——live、归 `experiments/` + 手测 runbook，不进 CI。

## 不变量 → 测试映射（覆盖保证）

| 全局不变量 / 关键契约 | 覆盖层 | Phase |
|---|---|---|
| 纯叠加、零侵入原生加载链 | system（管道不碰 loader）+ live 端到端 | 5,7 |
| validate-before-ANY-write（reject 零落盘） | unit + 集成 | 2 |
| 模型只 propose、land 确定性独占（无工具可跳） | unit（能力面）+ 红队 | 2,3 |
| REF 不自审（author≠validator） | 结构（reflector 工具集）+ promoter 独立校验 | 2,5 |
| 精确/安全→确定性，判断→LLM | unit（确定性侧）+ live（LLM 侧） | 1,2,5 |
| skills_guard self-produced 默认开 | 红队 unit | 1,2 |
| 只动自产（created_by 收口） | unit（modify 非自产 reject） | 2 |
| 原子 land（temp+os.replace，无半态/无 staging） | 集成（崩溃注入） | 2 |
| 调用率 + 缓刑 + 容量竞争 | unit + 集成 | 6 |
| 触发节奏==喂窗（零重叠） | unit | 4 |
| 崩溃 fail-safe（durable 队列 + at-least-once） | 集成（失败注入） | 2 |
| 平台机制（hook/MCP/Skill/transcript 真生效） | **live spike**（不进 CI） | 0 |

## 依赖与门禁

- Phase 0 的 spike 结论门禁 Phase 3/5/6 的 live 部分与投递形态；其确定性部分（schema、拼装、率算）不等 spike、可先建先测。
- CI 只跑确定性 + 管道（unit+system），live 全排除——**确定性侧零外部依赖即可全绿**，是合并门禁的实际内容。
- config 标定值（成熟阈值 / 上限 / `reflect_every_n`）经验标定走 `experiments/`，测试断言关系不断绝对值。
