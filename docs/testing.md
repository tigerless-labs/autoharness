# testing — conventions and the per-file test map

仓库目前无 pytest；Python 以 `experiments/` 下独立可运行脚本为约定。文档完整性由 `tools/` 下独立校验器守护：每个 `python3` 直接可跑、带 `--selftest` 对抗自检，断言**不变量**（链接可解析、frontmatter 合规），而非硬编码值。

## Checkers（提交前运行）

- `python3 tools/check_doc_links.py docs` — 全仓相对 `.md` 链接无悬空。**已知基线**：3 条 `DEFINITION.md` 悬空为 pre-existing（见 `docs/TODO.md`），解决前该检查对全仓非零退出；研判时只看"是否新增悬空"。
- `python3 tools/check_research_loom.py docs/research-loom` — research-loom 各层原子（`ideas/` `design/` `decisions/` `synthesis/` 中带 frontmatter 者）的契约：必填字段 + `status` 枚举。
- 每个 checker 的 `--selftest` 跑内置对抗用例（注入悬空链接 / 缺字段 / 越界枚举 → 必须报错）。

## Per-file map

| 产物 | 校验器 |
|---|---|
| `docs/**` 链接完整性 | `tools/check_doc_links.py` |
| `docs/research-loom/**` frontmatter 契约 | `tools/check_research_loom.py` |

> **TODO**: 产品代码落地后补 `tests/test_<module>.py` 与（若引入）pytest 约定：fixtures over live services、断言关系/不变量、对抗用例。
