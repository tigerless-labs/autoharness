# docs/plans —— 每次变更的实现计划

工作产物，每个非平凡变更对应一份。豁免于设计文档的风格规则。计划的第一个单元更新相关的 `docs/design/` 文档；每个单元都把测试置于代码之前。

- [roadmap.md](roadmap.md) —— 实现执行顺序 + 测试策略：自底向上构建（Phase 0 平台 spike → lib 地基 → promoter 闸 → CAP/REF/MNG → plugin 打包），三层测试（unit / system-fake-reflector / live spike）+ 不变量×测试映射 + CI 门禁；以 [architecture](../research-loom/design/architecture.md) 为准。
- [research-loom.md](research-loom.md) —— 文献→设计 合成流水线：`research-loom` skill（方法）+ `docs/research-loom/` 五阶段内容区（含 `research_results/` 全量迁移）。
