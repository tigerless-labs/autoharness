# plan — Phase 5：reflector 子代理 + spawn

> 工作艺术品（非设计文档）。装配自 [roadmap](roadmap.md) Phase 5 +
> [reflector-subagent](../research-loom/design/reflector-subagent.md) / [cap](../research-loom/design/cap.md) /
> [architecture](../research-loom/design/architecture.md)。每单元 docs→tests→code、tests 先于 code。

## 范围

交付 REF 的运行载体与启动器，**确定性侧全覆盖**（unit + system，fake reflector 驱动），活宿主行为留 live spike（不进 CI）：

1. `hook/spawn.py` —— 确定性拼装三件套（脱敏 episode 窗 + 现有 skill 描述索引 + 单一来源 `format_spec`）→ detached spawn 子会话 → 子会话完接 `promoter.drain`。
2. `agents/reflector.md` —— subagent 定义：最小权限工具集（`Read`/`Grep`/`Glob`/`stage_skill`，去 `Write`/`Edit`/`Bash`）+ compare-first review/authoring 正文（借 Hermes review-fork prompt 蓝本）。
3. `config.py` —— 补 spawn 旋钮指针（reflector agent 引用、claude 可执行名、子进程注入的 run_id/root 环境变量名），单点。

**不在本 Phase**：detached-from-host 的 hook 顶层后台启动（属 Phase 7 dispatch）；transcript 上界 race 精确化（cap.md 待解，v0 容忍）；reflector 真行为质量与 `PreToolUse` backstop 真 deny（live spike）。

## 单元

### U1 docs — 钉 spawn 拼装契约 + 解 `format_spec` 注入待解
- `reflector-subagent.md`：加「spawn 拼装」节——三件套来源、跨进程走磁盘、run_id/root 经环境注入、spawn 后接 promoter；定 `format_spec` **由 spawn 运行时注入 reflector 输入**（与 episode/描述索引同路），消掉 agent 静态正文里的第二份拷贝。
- `architecture.md`：§待解「`format_spec` 怎么进 reflector 正文」→ 落为决策（spawn 注入、单一来源不漂移）。

### U2 tests+code — `config` spawn 指针
- test：新增旋钮存在且类型对（agent 引用非空 str、env 变量名非空且互异）。
- code：`REFLECTOR_AGENT` / `CLAUDE_BIN` / `RUN_ID_ENV` / `PROJECT_ROOT_ENV`。

### U3 tests+code — `spawn` 确定性拼装（unit）
- `description_index(roots)`：枚举两层 live skill 树（跳 `.archive`），逐 `SKILL.md` 取 frontmatter `name`+`description`（复用 `validate` 的 frontmatter 解析，DRY）→ compare-first 索引串；空树→显式占位。
- `build_bundle(window, index, spec)`：三件套三段注入，三者俱在。
- `build_command(*, agent, claude_bin)`：argv 含 `--agent <ref>`、print 模式；prompt 走 stdin（大窗不塞 argv）。
- `child_env(run_id, root)`：置递归 guard 信号 + run_id/root 注入；不污染父环境。

### U4 tests+code — `spawn.run` 编排 + system 全链
- unit：`run` 注入 `spawn_fn`（替真 claude），断言三件套落盘 + 子进程拿到正确 env + 末尾调 `promoter.drain`。
- **system（fake reflector，真子进程、真磁盘）**：`spawn_fn` 实跑一个 fake reflector 脚本，脚本经环境拿 run_id/root、调 `stage_skill` append canned intent 进队列；`run` drain 后断言终态符号 + sidecar + LED 既成事实入账。证 CAP→spawn→promoter 跨进程闭环。

### U5 tests+code — `agents/reflector.md` 最小权限结构守卫
- test：reflector.md frontmatter 工具集 = `{Read,Grep,Glob,stage_skill}`，**不含** `Write`/`Edit`/`Bash`（author≠validator / least-privilege 不变量的确定性守卫）。
- code：写 `agents/reflector.md`（frontmatter 最小权限 + 便宜模型 + compare-first 正文）。

### U6 verify + sweep
- `pytest -m "not live"` 全绿；`python3 tools/check_doc_links.py docs` 绿。
- TODO 勾掉本 Phase 落项（reflector 正文借 Hermes、CAP 触发→spawn 接），保留真延期的 live spike 项。
- 扫 `docs/research-loom/design/index.md` 是否需更新。

## 测试映射（roadmap 不变量）
- 「REF 不自审（author≠validator）」→ U5 结构（工具集无写）+ promoter 独立校验（Phase 2 已覆）。
- 「纯叠加、零侵入」→ U4 system（管道不碰 loader，只 append 队列 + promoter 落盘）。
- 「触发节奏==喂窗」→ Phase 4 已覆；本 Phase spawn 只消费 CAP 物化窗，不重定。
