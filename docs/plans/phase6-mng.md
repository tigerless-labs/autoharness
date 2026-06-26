# plan — Phase 6：MNG 生命周期

> 工作艺术品（非设计文档）。装配自 [roadmap](roadmap.md) Phase 6 + [mng](../research-loom/design/mng.md)。
> 每单元 docs→tests→code、tests 先于 code。

## 范围

确定性生命周期：调用率定生死、缓刑护新、容量竞争、惰性 `SessionStart` 现算、archived 移目录出召回（可逆）。复用 Phase 1 的 `counters`（层请求分母）/ `sidecar`（calls 分子 + anchor）/ `skill_store`（archive）。

1. `lib/lifecycle.py` —— 纯确定性判定：成员→(分母=层请求−锚, 率=calls/分母)→缓刑/毕业/毕业即审/容量竞争→产「待归档名单」。不碰盘。
2. `lib/skill_store.py` —— 补 `restore`（archive 的逆：`.archive/<name>` 移回 live），落「移回复活（可逆）」。
3. `hook/on_skill_call.py` —— `PreToolUse(Skill)` 分子 +1：解析被调符号→层定位→**仅自产符号** bump_calls（零侵入：绝不给原生 / 用户 skill 写 sidecar）+ 递归 guard。
4. `hook/on_session_start.py` —— 惰性重算：每层收成员 sidecar + 层请求数 + config 阈值/上限 → lifecycle 判定 → 逐个 archive。判定只读累积水位（跨 session / 跨 repo 同结论）。

**不在本 Phase（留 TODO）**：CAP 孤儿会话计数 GC——`clear_session` 原语已备（Phase 4），但「哪个 session 是孤儿」需会话存活信号，朴素扫删会误删并发会话的活计数；缺信号前不实现（concurrency-unsafe）。绝对底线规则（毕业审外的硬底线 Y）、滚动窗口率、global 并发写锁、覆盖盲区——mng.md 待解，留后。

## 单元

### U1 docs
mng.md 已完整钉死率/缓刑/容量/触发/可逆——无新设计事实，**不改**（守 docs 简洁律）。仅 U5 扫 index/TODO。

### U2 tests+code — `lifecycle.evaluate`（纯函数）+ `skill_store.restore`
- `evaluate(members, request_count, *, maturity, capacity)` → 待归档名单：
  - 分母 = `max(0, request_count − anchor)`；分母 < maturity → 缓刑（live、不淘汰、不占上限）。
  - 毕业（分母 ≥ maturity）：calls==0 → 毕业即审当场归档。
  - 成熟存活池（calls>0）超 capacity → 按 (率升序, name) 归档最低者至回上限内。
- test 断言**不变量**：缓刑符号永不入归档；calls==0 毕业即归档；成熟超容按率序淘汰最低、不淘汰高率；分母随 request_count 增长（关系非绝对值）；tie 用 name 稳定。
- `restore`：`.archive/<name>` 原子移回 `skills/<name>`，sidecar 随迁；archive→restore 往返后 live 存在、归档区空（可逆）。

### U3 tests+code — `on_skill_call`（分子埋点）
- 自产符号被调 → 其 sidecar calls +1（层由 find 解析）。
- **非自产 / 原生符号被调 → 不写 sidecar**（零侵入红线，最关键红队点）。
- 递归 guard（CHILD_SESSION_ENV 有值早退、不计）；坏/缺符号名 fail-safe 不崩。

### U4 tests+code — `on_session_start`（惰性重算，集成 `tmp_path`）
- 多符号跨缓刑/成熟/零调，跑 handler → 该归档的移出 live 树、该留的留；archived 不在 live、可 restore 复活。
- 判定只读 sidecar + 层请求计数器累积水位 → 任意 root 的 SessionStart 同结论（喂同账两次得同果）。
- 复用 promoter 的 `.tmp` sweep？on_session_start 只管 MNG；`.tmp` 孤儿已由 promoter.drain sweep，不重复。

### U5 verify + sweep
- `pytest -m "not live"` 全绿；doc checkers 绿。
- TODO：勾「delete 归档退役编排属 Phase 6」相关、补「孤儿会话 GC 仍缺存活信号」延期说明。扫 design/index.md（mng 条目已在，确认无需改）。

## 测试映射（roadmap 不变量）
- 「调用率 + 缓刑 + 容量竞争」→ U2 unit。
- 「archived 移目录出召回、可逆」→ U2 restore + U4 集成。
- 「判定读累积水位、任意 repo 同结论」→ U4。
- 「零侵入：不碰原生 / 用户 skill」→ U3 红队（非自产不写 sidecar）。
- 「MNG handler 挂单一 dispatcher、零 daemon」→ 结构（handler 是纯函数、SessionStart 现算，无常驻）；dispatch 路由 Phase 7。
