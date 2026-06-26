# E7 — plugin 端到端手测（live，不进 CI）

验证打包后的 plugin 在真 Claude Code 里跑通捕获→反思→准入→召回的全闭环。确定性侧（dispatch 路由、
MCP 外壳、清单合法）已由 `tests/test_dispatch.py` `tests/test_stage_skill.py` `tests/test_manifests.py`
覆盖；本 runbook 只验**平台真生效**部分（hook/MCP/Skill/transcript），结论回填 `results.md`。

## 隔离沙箱（绝不污染真实 `~/.claude`）

plugin 真往两层写：global `~/.claude/skills`、repo `./.claude/skills`。手测**必须隔离盘**，否则会
往你真实的 skills + 本 plugin 自身里写。

```
export HOME=$(mktemp -d)              # 隔离 global 层（先确认宿主认 HOME 重定向；不认则退 Docker 干净宿主）
mkdir -p "$HOME/sandbox-repo" && cd "$HOME/sandbox-repo" && git init -q
# 本地装（不走已发布 marketplace）：把本仓作单 plugin marketplace
/plugin marketplace add /path/to/autoharness
/plugin install autoharness@autoharness
```

## 调小旋钮（短会话内跑出毕业 / 容量竞争）

config 经 `AUTOHARNESS_*` env 覆盖（缺省回占位）。装前 export，让一次手测就能触发反思 + 毕业 + 淘汰：

```
export AUTOHARNESS_REFLECT_EVERY_N=2     # 2 轮即触发一次反思
export AUTOHARNESS_MATURITY_PROJECT=2    # 2 次请求即毕业（出缓刑）
export AUTOHARNESS_CAPACITY_PROJECT=1    # 容量 1：塞 2 个符号即逼出容量竞争
```

## 装

```
/plugin marketplace add tigerless-labs/autoharness
/plugin install autoharness@autoharness
```

重启 Claude Code 激活。

## 验注册

```
/mcp
```

- `stage_skill` MCP 在列且 connected。
- `/hooks` 显示 SessionStart / Stop / PreToolUse(Skill) / SessionEnd 均指向单一 `dispatch`。

## 跑闭环（4 拍）

1. **生**：做一段会重复某操作的真实任务，连续 `Stop` 满 `AUTOHARNESS_REFLECT_EVERY_N` 触发反思；确认后台 detached reflector 子会话起、未堵宿主 `Stop`（宿主立即可继续输入）。
2. **用**：新会话里调起刚学的符号 → `PreToolUse(Skill)` 经 dispatch 给其 sidecar 分子 +1。
3. **争**：再造一个低用符号；两符号成熟、容量 1 → `SessionStart` 重算按率归档最低者。
4. **审**：重启会话触发 `SessionStart` 惰性现算。

## 验结果（断言盘上终态，不靠模型自述）

- 符号落 `$HOME/sandbox-repo/.claude/skills/<name>/SKILL.md`，内容过 promoter 六类校验。
- 新会话里该符号经**原生 name+description 召回**注入（非本 plugin 改加载链）。
- `<name>` 的 sidecar 记 `created_by:agent` + LED `create` 条目（reason/evidence/anchor）+ calls 计数随调用涨。
- 被淘汰符号移进 `.claude/skills/.archive/`、新会话不再注入；`restore` 后复活。
- reflector 子会话的 `Stop` 转 `SubagentStop` + `CLAUDE_CODE_CHILD_SESSION` 递归 guard → 不二次触发。

## 门禁（Phase 0 已闭，见 [E6](../E6_platform_contracts/results.md)）

S1–S6 已闭：plugin agent 不认 `hooks`/`mcpServers` frontmatter（S1）→ backstop + stage_skill **已退顶层**（本投递形态）；deny=exit2/JSON（S3）；Skill 走 `PreToolUse(Skill)`、身份在 `tool_input`（S5）；`Stop`=每回合（S6）。本 runbook 验的是这些契约在**装好的 plugin** 里端到端真生效，非再验契约本身。

剩观测项：`${CLAUDE_PLUGIN_ROOT}/src` 上 `python3` 与宿主 Python 环境一致性（无 pyproject、靠 PYTHONPATH）；HOME 重定向是否真隔离 global 层（不隔则退 Docker）。

结论 + 截图 → `results.md`。
