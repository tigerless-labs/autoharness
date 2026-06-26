# Phase 2 — promoter 校验·存储（admission 闸）

设计权威：[validate-store](../research-loom/design/validate-store.md)。本文只记实现切分，不重述设计。

## 交付物

- `hook/promoter.py` —— 唯一确定性写者。`promote(intent)` 处理单条 intent：成型 → 校验 → 落盘/拒；
  `drain(run_id)` 读队列逐条 promote、末尾 clear（at-least-once）；`sweep()` 启动扫孤儿 `.tmp`。
- `lib/skill_store.archive` —— delete 落地的「归档」原语（移 symbol_dir 进 `.archive`，保 LED/sidecar），
  MNG（Phase 6）复用。
- `lib/validate` 补 delete：body 为空时跳过依赖 body 的四类（安全/结构/完整/global），只留 LED + 自产。

## 单元（数据依赖自底向上）

1. **skill_store.archive** —— 移走保账本、目标已存在则覆盖、不存在返 None。
2. **validate delete** —— body=None 只查 LED + 自产；create/update/patch 行为不变。
3. **promoter.promote** —— 四 action：
   - 成型：create/update=intent body；patch=live+delta 重建；delete=None。
   - 层解析：create 取 intent `level`；update/patch/delete 走 `skill_store.find`（同名跨层报错、缺失拒）。
   - 校验：喂 `{**intent, level:解析层}`（global 闸对 update 也生效）+ 自产标志（读 sidecar）+ base_dir（symbol_dir）。
   - pass：写 body（原子）→ create 盖 sidecar `created_by:agent` → append intent 自带 LED；delete=LED 退役 + archive。
   - reject：零落盘、不打标、不入账。
4. **promoter.drain / sweep** —— 队列驱动 + 崩溃补处理。

## 不变量 / 红队（断言）

reject 后盘上零变化；原子 rename 无半态；孤儿 `.tmp` 启动 swept；patch 由 live+delta 重建；
`update/patch/delete` 目标非 `created_by:agent` → reject；缺 LED → reject；含 TODO/占位符 → reject；
global 含 repo-local → reject；create 过六类才打标、未过不打标；投毒/注入正文被 skills_guard 挡；
模型无 commit 工具面（只塞 intent）；崩溃下 intent 留队列、补处理幂等、极端零 land（fail-safe）。

## 范围外（记 TODO，留后）

watermark（Phase 4 CAP 供）；create 锚 `anchor`（v1 由调用方入参、缺省 0，CAP 供真值）；
跨进程单写者锁（mng 待解）；LED 逐条幂等 watermark（v1 整 run clear、崩溃极窗可重 append）；
validate #416 引用文件存在性 / 断 symlink（intent 带显式文件清单再加）。
