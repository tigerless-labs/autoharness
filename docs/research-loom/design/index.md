# design — ④ 装配（设计草稿 + provenance）

把永久笔记织成设计，每个设计元素经相对链接连起 provenance：**设计元素 → [ideas/](../ideas/index.md) → 来源卡**。设计分两类文件：脊柱一篇（原则+流水线+全局不变量+架构图）+ 每步/模块各一篇（行为边界+接口契约+验收）。过渡期此处为将来唯一设计家；现有 `docs/design/` 冻结为 legacy，以此处为准。方法由 `research-loom` skill 承载。

- 🦴 **[spine — autoharness workflow v0](spine.md)** — 系统架构图：宿主 + 学习管道（CAP→REF→ADM→STO→INJ）+ 注入回路 + 生命周期分支（MNG）+ 账本（LED）；含组件职责 / 决策 / 待解。

> per-step / per-模块 文档待补：动哪一步、补哪一篇（lifecycle docs-first）。`STO` 生死与 `RPL` 降级待开 [decisions/](../decisions/index.md)。
