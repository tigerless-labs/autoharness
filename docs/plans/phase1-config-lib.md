# plan — Phase 1：config + `lib/` write-once 原语（地基）

> 工作艺术品，非设计文档。落地 [roadmap](roadmap.md) Phase 1。契约源：
> [architecture](../research-loom/design/architecture.md)（代码落位）、
> [validate-store](../research-loom/design/validate-store.md)、[cap](../research-loom/design/cap.md)、
> [mng](../research-loom/design/mng.md)、[stage-skill](../research-loom/design/stage-skill.md)。

## 范围

`src/autoharness/config.py` + `src/autoharness/lib/` 九原语 + 两份契约数据。**不含 `lifecycle`**
（Phase 6）。全纯确定性、全管道复用、`layer` 只作入参不分叉代码。测试住仓库根 `tests/test_<module>.py`，
`pytest.ini` 的 `pythonpath=src` 让其 import `autoharness.*`。

## 落盘约定（architecture §运行时数据）

两层、各一 root：`global`=`~/.claude`，`project`=`<cwd>/.claude`。各层下 `skills/<symbol>/`、
`skills/.archive/<symbol>/`、`autoharness/`（状态区，git-ignored）。`layer.py` 是唯一路径解析处；
`config.py` 持分层旋钮值。两层名定为 **`global` / `project`**（对齐 stage_skill 的 `level` enum）。

## 构建顺序（自底向上，每片 test-first → 绿 → commit）

1. **config + layer** —— 旋钮单点（`reflect_every_n` / 成熟阈值·容量两层各设 / 红线集·format_spec 指针）；
   `layer` 由层名解析落盘位、拒未知层（fail-safe）。
2. **契约数据 + 消费者** —— `redaction_rules.toml`（secret/PII，CAP egress + LED 同源）+ `redact`
   （消费红线、物化那刻切片脱敏）；`skills_guard`（六族正则 exfiltration/injection/destructive/
   persistence/network/obfuscation，self-produced 默认开、强化 injection）；`format_spec.md`
   （#416 必填结构契约，REF 写 + linter 验同源）。
2. **符号状态** —— `sidecar`（created_by / 分子计数 / 创建锚 / verification，单一实现、随符号目录走层）；
   `ledger`（LED append-only、只增不改）；`counters`（会话计数 + 层请求计数，O(1) 读改写）。
3. **store + 队列 + validate** —— `skill_store`（原子写 temp+`os.replace` + 两层 find、同名跨层报错消歧 +
   应用 delta）；`intent_queue`（append=stage_skill / drain=promoter / 启动 sweep 孤儿，durable）；
   `validate`（六类 linter 跑在内存成型结果上，复用 skills_guard + format_spec + sidecar）。

## 断言什么（roadmap 测试三层的 unit 行）

关系 / 不变量，非硬编码值：`layer` 两层路径不相交、未知层 reject；`skill_store` 原子写无半态、同名跨两层
find 报错；`sidecar` 单实现读写往返一致；`ledger` 只增不改（append-only）；`intent_queue` append→drain
往返、孤儿 sweep；`counters` +1 往返、按层独立、O(1)；`redact` 不漏 PII/secret；`validate` 六类各自挡；
`skills_guard` 六族各命中。**红队**：skills_guard 挡投毒/指令型注入；redact 不漏；global 含 repo-local
被 validate 降级/reject。config 标定值只断言关系（两层俱在、>0、指针文件存在），绝对值留 `experiments/` 标定。

## 待解（落 TODO）

- `intent_queue` 持久格式/粒度：先最小 durable（崩溃补处理、处理完删），与 validate-store 待解同。
- config 成熟阈值/容量默认值经验标定走 `experiments/`。
