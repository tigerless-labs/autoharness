# Phase 3 — stage_skill MCP（emit-intent 提案面）实现计划

> 工作艺术品。设计权威：[stage-skill](../research-loom/design/stage-skill.md)、落位 [architecture](../research-loom/design/architecture.md)、顺序 [roadmap](roadmap.md) §Phase 3。

## 交付物

`src/autoharness/stage_skill/server.py` —— reflector 的唯一写入面。职责三件、缺一不可：

1. **schema 强制结构**：`action` enum（create/update/patch/delete）；按 action 的 `body | delta` 互斥与必填；LED 字段 `reason`/`evidence` 必填；create 的 `level` enum（默认 project）。
2. **入参即时反馈**：复用 Phase 1 `validate` 的结构查（frontmatter + name/description）+ 内容大小，给当场反馈，让模型在 subagent 会话内改、不整轮重来。
3. **只 append intent 队列**：成型 / 内容 / 安全 / 落盘全不碰——那是 [promoter](../research-loom/design/validate-store.md) 的事。append 的 intent 形状与 `promoter.promote` 消费的一致（patch 走顶层 `old_string`/`new_string`）。

## ponytail 上限：MCP 进程绑定缓 Phase 7

零外部依赖铁律禁止引官方 `mcp` SDK；MCP 工具能否 scope 到单 subagent 又是未决的 Phase 0 spike。故本 Phase 只交付**确定性、可 CI 测的工具处理器**（schema + 反馈 + append）；stdio JSON-RPC 进程外壳（`serve()`）随 Phase 7 打包落地、待 Phase 0 MCP-scope 结论定形。`server.py` 暴露 `TOOL_SCHEMA`（对模型广告的入参面）与 `stage()`（强制权威）。

## 单元（每单元 tests 先于 code）

1. **docs + config**：stage-skill.md 待解补「wire 缓 Phase 7」；`config.py` 加 `STAGE_MAX_BODY_BYTES`（ponytail 占位）；`validate.py` 暴露 `structure()` 公开复用点（消跨模块私有触达）。
2. **schema 强制**（tests→code）：未知 action / 缺 LED / `body`+`delta` 互斥违例 / patch 缺 `old_string`|`new_string` / delete 带 body / create 越界 level → 全 reject、零 append。
3. **即时反馈 + append**（tests→code）：create body 缺 frontmatter / 超大 → reject 零 append；合规 → append、`intent_queue.read` 取到、且**宿主 skill 树零变化**（`skills_dir` 不存在）。

## 不变量 / 红队

- **模型结构上 land 不了**：`stage()` 全路径无任何 skill 树写——成功 append 后断言 `layer.skills_dir(project)` 不存在。
- **LED 入参即保证**：缺 `reason`/`evidence` → reject，intent 进不了队列 → promoter 的「LED 有没有」近乎不可违。
- **不安全 run_id**：`intent_queue.append` 抛 → `stage()` 兜成 error 返回、不崩。
- tool 只前置**结构**；内容 / 交叉引用 / 安全 / 成型 / 落盘**不在此**（promoter 兜，防御纵深）。

## 范围外 / TODO

- MCP stdio `serve()` 外壳 + `.mcp.json` 注册 → Phase 7（见 ceiling）。
- run_id / root 由 spawn 经环境注入 → Phase 5 wiring；本 Phase `stage()` 收作入参。
- MCP 只 reflector 可见、入参校验失败的当场改闭环 → Phase 0 live spike。
