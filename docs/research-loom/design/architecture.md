---
id: architecture
type: design
---
# 代码架构：autoharness 作为单个 Claude Code plugin

最终形态是**一个可经 marketplace 安装的 Claude Code plugin**。三条铁律定全局：**代码只一份**——住 plugin、装到 `~/.claude/plugins/cache/`，host-agnostic、跨仓共用，绝不按层复制；**执行只从 plugin 的 hook 全局层发起**——官方单 dispatcher 模式，凡 pipeline 的执行步都收进这一个大模块；**只有数据/状态分 global/repo**——落宿主对应目录。config 单点，更新/维护逻辑 write-once、层只作入参。各步行为边界见 [spine](spine.md) 与 per-module 文档，本文只定**代码怎么摆**。

## 文件树（plugin = 代码唯一家）

```
autoharness/                         # plugin 根（装到 ~/.claude/plugins/cache/autoharness）
├── .claude-plugin/
│   └── plugin.json                  # 清单：名称 / 版本 / 组件登记
├── hooks/
│   └── hooks.json                   # 把所有事件 → 单一 dispatcher（${CLAUDE_PLUGIN_ROOT}）
├── agents/
│   └── reflector.md                 # REF 运行载体；tools 收窄到 Read / Grep / Glob / stage_skill
├── .mcp.json                        # 登记 stage_skill MCP（reflector 的写专用面）
└── src/autoharness/                 # ★ 代码唯一家（单份、跨层共用，layer 只作入参）
    ├── config.py                    # ★ 全部旋钮单点：节奏 / 成熟阈值 / 上限(分层) / 红线集 / format spec 指针
    ├── hook/                        # ★ 唯一执行层：hook 操作 + 被其驱动的 pipeline 步，全在此一个大模块
    │   ├── dispatch.py              #     单入口：按事件名路由（hooks.json 只指它）
    │   ├── on_stop.py               #     CAP 触发：递归 guard + 计数闸
    │   ├── on_session_end.py        #     CAP flush 余量
    │   ├── on_session_start.py      #     MNG 惰性重算 + 孤儿 / .tmp GC
    │   ├── on_skill_call.py         #     MNG 分子 +1（PreToolUse(Skill) 埋点）
    │   ├── capture.py               #     CAP 步：指针索引 + egress 脱敏 + tail-N 物化
    │   ├── spawn.py                 #     确定性拼装 reflector 输入(episode 窗 + 描述索引 + format_spec) → detached spawn → 返回接 promoter
    │   └── promoter.py              #     校验·存储步：内存成型 → 内存校验 → 原子落盘
    ├── stage_skill/
    │   └── server.py                #   MCP server：emit-intent，schema 强制结构 + LED 字段
    └── lib/                         # ★ write-once 维护原语（hook 层与 stage_skill 共用同一份）
        ├── layer.py                 #   由 layer 入参解析 global / repo 落盘位（层显形处之一：路径）
        ├── skill_store.py           #   skill CRUD：原子写 + 两层 find + 应用 delta
        ├── sidecar.py               #   sidecar 读写：created_by / 计数 / verification（单一实现）
        ├── ledger.py                #   LED append-only
        ├── intent_queue.py          #   per-run intent 队列：append(stage_skill)/ drain(promoter)/ 启动 sweep 孤儿（持久策略见 validate-store 待解，先最小）
        ├── counters.py              #   CAP 会话计数 + MNG 分子 / 分母（单一实现、按层）
        ├── lifecycle.py             #   MNG：率 + 缓刑 + 容量竞争
        ├── validate.py              #   确定性 linter 六类（含自产标签）
        ├── skills_guard.py          #   安全正则扫描
        ├── redact.py                #   egress 红线集消费者
        └── format_spec.md           #   authoring / lint 单一契约（REF 按它写、linter 按它验）
```

## 运行时数据（唯一分层的东西，plugin 不持有）

代码以外的一切落宿主，按 storage 类型分两层；状态区 git-ignored，**绝不入 live `skills/` 或 intent 队列以外的盘**。

```
~/.claude/                           # global 层
├── skills/<symbol>/                 #   live 符号(global) + 每符号 sidecar（LED / created_by / 计数）
├── skills/.archive/<symbol>/        #   归档(global)：MNG 移出 live、不删除、可复活（sidecar 随迁）
└── autoharness/                     #   global 请求计数器（跨仓共写）
./.claude/                           # repo 层（git-ignored）
├── skills/<symbol>/                 #   live 符号(project) + sidecar
├── skills/.archive/<symbol>/        #   归档(project)：同上
└── autoharness/                     #   CAP 会话计数器 + repo 请求计数器 + per-run intent 队列 + 孤儿 .tmp
```

## 四条结构轴

- **代码单份 vs 数据分层**：`skill_store` / `sidecar` / `counters` / `lifecycle` 全是一份实现，global 与 repo 走**同一函数**，只把 `layer` 入参喂给 `layer.py` 算落盘位——消灭"两套维护逻辑"。**代码逻辑层无关；层只在两处显形：`layer.py` 解析路径、`config` 持分层旋钮值（成熟阈值 / 上限两层各一）**。
- **执行只在 hook 全局层**：`hook/` 是唯一一个大执行模块，`dispatch` 单入口、每事件一个 `on_*` 文件（CAP 与 MNG 的 handler 都挂这里，**不另起 hook 注册**）、各执行步一个文件（`capture` 属 CAP、`spawn` 是 **REF 的启动载体**、`promoter` 属校验·存储）。`hooks.json` 只指 `dispatch`，决不在别处自起执行。`stage_skill` 因是 reflector 调用的独立 MCP 进程而单列，不属此模块。
- **config 单点**：`config.py` 是所有旋钮的唯一家——触发节奏、成熟阈值、容量上限（两层各一）、红线集与 format spec 的指针。红线集（CAP egress 与 LED 共用）、format spec（REF authoring 与 #416 linter 共用）各自是**单一来源**，由 config 指向、两处消费。
- **维护 write-once、层作入参**：凡"增 / 删 / 改 / 归档 / 计数 / 退役"的逻辑只在 `lib/` 写一次；promoter 的落盘、MNG 的淘汰、CAP 的计数都复用它，按 `layer` 参数化，不复制。

## spine 模块落位

| 模块 | 代码落位 | per-module |
|---|---|---|
| CAP 捕获 | `hook/{on_stop,on_session_end,capture}` + `lib/{counters,redact}` | [cap](cap.md) |
| REF 反思 | `agents/reflector.md`（定义） | [ref](ref.md) · [reflector-subagent](reflector-subagent.md) |
| stage_skill | `stage_skill/server.py` + 复用 `lib/{skill_store,validate,intent_queue}` | [stage-skill](stage-skill.md) |
| 校验·存储 | `hook/promoter.py` + `lib/{skill_store,validate,skills_guard,ledger,sidecar,intent_queue}` | [validate-store](validate-store.md) |
| MNG 生命周期 | `hook/on_session_start.py` + `lib/{lifecycle,counters,sidecar}` | [mng](mng.md) |
| LED 账本 | `lib/{ledger,sidecar}` | （per-module 待补） |

## 决策

- 代码不按层 fork：`layer` 是 `lib/` 的入参、不是代码分叉点；global / repo 共用同一套维护原语。
- 执行全收进 `hook/` 一个大模块（`dispatch` 单入口 + 子文件）；`stage_skill` 因独立 MCP 进程单列，是唯一例外。
- `config.py` 单文件持全部旋钮（含分层上限 / 阈值）；红线集与 format spec 由 config 指向各自单一来源，多处只消费。
- 数据按 storage 分 global / repo 落宿主对应目录；状态区 git-ignored，不入 live skills。
- src 锁 Python（与 `tools/` `experiments/` 一致），通过 plugin 分发、不污染宿主项目。
- **测试只住仓库根 `tests/`**：按 `tests/test_<module>.py` 镜像 `src/autoharness/` 各模块，**不放进 plugin 树、不随 plugin 分发**（`pytest.ini` 的 `testpaths=tests` 物理封死收集范围）。依赖活宿主的用例 `@pytest.mark.live` 标记、CI 排除；执行顺序与三层测试策略见 [roadmap](../../plans/roadmap.md)。
- 投递走**自建 marketplace**（一个含 `marketplace.json` 的 GitHub repo，用户 `/plugin marketplace add` 即装，无审核）；不追官方策展 marketplace。瓶颈不在上架，在"装后能跑 + 可信"。

## 待解 / 动手前实测

- **plugin-shipped agent 是否支持 `hooks` / `mcpServers` frontmatter**：有资料称出于安全**不支持**。若属实，[reflector-subagent](reflector-subagent.md) 的"自带 PreToolUse backstop"与 [stage-skill](stage-skill.md) 的 subagent-scoped 注册都得改投递——backstop 退到 plugin 顶层 `hooks/hooks.json`、stage_skill 退到顶层 `.mcp.json` 再运行时 scope。先实测确认，再定 `agents/reflector.md` 能装多少。
- **首次运行初始化**（marketplace 已定自建，见决策）：plugin 装好后组件（`agents/` `hooks/` `.mcp.json`）随 plugin 就位、**不另拷**（`reflector.md` 是 plugin 内组件，不进用户 `~/.claude/agents/`）；两层数据区（`~/.claude/skills`、`./.claude/autoharness` 等）首写时惰性建即可，是否要显式 init 脚本待定。`hooks.json` 用 `${CLAUDE_PLUGIN_ROOT}` 自定位是 plugin 机制、非安装动作。
- **`hook/` 与 `lib/` 的进程边界**：每个 hook fire 是独立短进程，`lib/` 的计数 / 落盘必即时持久（内存留不住），与 promoter 的 durable intent 队列对齐。
- **`format_spec.md` 怎么进 reflector 正文**：它是 `lib/` 单一来源，要同时喂 reflector authoring（`agents/reflector.md` 系统提示）与 #416 linter。但 agent 正文是静态 md——投递机制未定（候选：spawn 拼 bundle 时把 `format_spec` 内容一并注入 reflector 输入，与 episode / 描述索引同路，省一份静态拷贝）；不钉死则"单一来源"有变两份漂移的风险。

---

provenance：装配自 [spine](spine.md) 的管道职责切分；零侵入 / 最小权限 / 只动自产约束见 [additive-over-native-skill](../ideas/additive-over-native-skill.md)；分层落盘见 [precipitate-storage-layer](../ideas/precipitate-storage-layer.md)。plugin / hooks.json / agent / MCP 的官方结构见 Claude Code plugins 文档（源卡待建）。
