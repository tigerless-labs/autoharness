# testing — conventions and the per-file test map

产品代码（`src/autoharness/`）以 pytest 测，每模块一份 `tests/test_<module>.py`、用 `tmp_path` fixture 不连外部服务、断言**关系/不变量**（reject 零落盘、原子 rename 无半态、率序）+ 红队用例（投毒挡、越权 reject、注入挡）；`experiments/` 下另有独立可运行脚本约定。文档完整性由 `tools/` 下独立校验器守护：每个 `python3` 直接可跑、带 `--selftest` 对抗自检，断言**不变量**（链接可解析、frontmatter 合规），而非硬编码值。

## Checkers（提交前运行）

- `python3 tools/check_doc_links.py docs` — 全仓相对 `.md` 链接无悬空。**已知基线**：3 条 `DEFINITION.md` 悬空为 pre-existing（见 `docs/TODO.md`），解决前该检查对全仓非零退出；研判时只看"是否新增悬空"。
- `python3 tools/check_research_loom.py docs/research-loom` — research-loom 各层原子（`ideas/` `design/` `decisions/` `synthesis/` 中带 frontmatter 者）的契约：必填字段 + `status` 枚举。
- 每个 checker 的 `--selftest` 跑内置对抗用例（注入悬空链接 / 缺字段 / 越界枚举 → 必须报错）。

## Per-file map

| 产物 | 校验器 |
|---|---|
| `docs/**` 链接完整性 | `tools/check_doc_links.py` |
| `docs/research-loom/**` frontmatter 契约 | `tools/check_research_loom.py` |
| `src/autoharness/<module>.py` | `tests/test_<module>.py`（pytest，`pytest -m "not live"`，`pythonpath = src`） |

> 活宿主依赖（LLM 反思质量、hook/MCP 真生效、Skill 真触发）走 `@pytest.mark.live`，CI 排除、靠 fake reflector 在 CI 里测管道接缝（见 [`docs/plans/roadmap.md`](plans/roadmap.md) 三层测试策略）。
