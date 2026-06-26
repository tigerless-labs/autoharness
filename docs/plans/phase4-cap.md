# Phase 4 — CAP 捕获 + 触发 实现计划

> 工作艺术品。设计权威：[cap](../research-loom/design/cap.md)、落位 [architecture](../research-loom/design/architecture.md)、顺序 [roadmap](roadmap.md) §Phase 4。

## 交付物

CAP = 哑管 + egress 脱敏 + 触发，全程确定性、不调 LLM。复用 Phase 1 `counters` / `redact` / `atomic`。

1. **`hook/capture.py`**（交什么）：触发那刻从宿主 transcript 取 tail-N exchange 窗 → 过 egress 红线（`redact`）→ 原子物化到 handoff 路径给 reflector 跨进程读。**零内容拷贝**（不触发不抄）、**绝不回写宿主 raw log**。
2. **`hook/on_stop.py`**（何时触发·每轮）：`CLAUDE_CODE_CHILD_SESSION` 有值即早退（递归 guard，且不计数）→ `bump_session` → 满 `reflect_every_n` 则 `reset_session` 并出触发裁决，未满退出。每 Stop O(1)、**不扫 transcript**。
3. **`hook/on_session_end.py`**（何时触发·收尾）：计数 > 0 即 flush 余量（窗口 N = 当前计数、非阈值），随后自删会话计数器。
4. **`counters.clear_session`**（最小扩展）：SessionEnd 自删用，unlink 缺失即忽略。

触发节奏 == 喂窗大小（同为 `reflect_every_n`）→ 计数器一物双用、零重叠。detached spawn 本身是 [reflector-subagent](../research-loom/design/reflector-subagent.md) 的载体、接 Phase 5 `spawn.py`；本 Phase 出**触发裁决 + 窗口 N**，spawn 据此调 `capture.materialize`。

## ponytail 上限

- **transcript 解析 = 宿主格式假设**：exchange 切分按「user 角色起新窗」、字段容错抽 role/text。真 Claude Code `.jsonl` schema + compaction 下 tail-N 是否取到原始轮次 = Phase 0 live spike（[cap](../research-loom/design/cap.md) 待解）。解析标 ceiling、按 fixture 测不变量、spike 定真格式。
- **spawn 调用**：on_stop/on_session_end 出裁决，不直接 detached spawn（Phase 5 `spawn.py` 接）。

## 单元（每单元 tests 先于 code）

1. `counters.clear_session`（tests→code）：unlink、缺失幂等。
2. `capture`（tests→code）：tmp transcript fixture → tail-N 取最近 N exchange；窗内 secret/PII 被 `redact`；`materialize` 原子写 handoff、**宿主 transcript 字节不变**；窗大小 == N（零重叠）。
3. `on_stop`（tests→code）：每 Stop +1；满 N 触发并清零；未满不触发；`CLAUDE_CODE_CHILD_SESSION` 早退**不 +1**（递归 guard）；裁决不带 transcript 扫描。
4. `on_session_end`（tests→code）：计数 > 0 → 触发、窗口 N == 计数；== 0 → 不触发；收尾后计数器文件已删。
5. 集成：N-1 个 Stop 不触发、第 N 个触发清零、再跑到 SessionEnd flush 尾巴。

## 不变量 / 红队

- **egress 脱敏在物化窗、非宿主 raw log**：materialize 后断言宿主 transcript 字节不变、handoff 窗已脱敏。
- **递归 guard**：child session 的 Stop 不计数、不触发 → reflector 自身 Stop 不致无限反思。
- **不扫 transcript 计数**：on_stop 只读改写小 int 计数器（O(1)），触发那刻才读一次 transcript 取窗。
- 不安全 session-id → `counters` 抛（已 Phase 1 测，CAP 复用同守卫）。

## 范围外 / TODO

- **`on_session_start` 孤儿计数 GC** → Phase 6（该文件在 MNG 建）；cap.md 已记「留待解」。
- **触发→读取 race**（满 N 到 detached 真读间又来 1~2 轮，tail-N 漏最老）→ v0 容忍，精确化随 spawn 带 transcript 上界（Phase 5）。
- **episode 边界信号**（task-done / token 预算）→ 未定，v0 攒够 N 近似（[ref](../research-loom/design/ref.md) 共享待解）。
