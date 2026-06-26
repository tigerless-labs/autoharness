---
id: spine
type: design
---
# 系统架构：autoharness workflow v0

autoharness 在 agent 的真实运行中积累经验、并就地验证经验：经验不靠一次离线 eval 拿快照分，而是靠在后续交互里持续被遵守、奏效挣得存活，被矛盾 / 失效则退役。

实现上，它在宿主 agent 之外**纯叠加**地运行：CAP 经 hooks 观察会话，REF **compare-first** 地把 episode 蒸馏成对齐现有库的改动、经 stage_skill 发成 **intent**（不落盘），**确定性 promoter（校验·存储）**内存成型 + 内存校验、过了才**原子落盘**进宿主 skill 目录（`.claude/skills`）走正常 description 召回；对原生 skill 加载链路零侵入。MNG 决定符号活多久，LED 记每次增删改的理由与证据。

```
┌──────────────── 宿主 agent（host-agnostic）— autoharness 纯叠加、零侵入 ────────────────┐
│      会话运行   ·   原生 skill 加载（.claude/skills；name+desc → description 概率召回）   │
└───┬──────────────────────────────────────────────────────────────────────▲────────────┘
    │ CAP 观察：hooks（仅此步用 hook）                    符号即原生 skill · 宿主正常召回 │
    ▼                                                                          │
┌─────────┐   ┌─────────────────────┐   ┌──────────────────────────────┐
│ CAP 捕获│──►│ REF 反思             │──►│ 校验·存储 promoter（admission）│──────────┘
│ (hooks) │   │ compare-first        │   │ 内存成型 create=body /         │
│         │   │ 经 stage_skill 发     │   │   patch=live+delta             │
│         │   │ intent(body|delta +   │   │ 内存校验 guard+#416+LED+完整   │
│         │   │ reason/evidence,不落盘)│   │ pass→temp+原子rename→live      │
│         │   └─────────────────────┘   │ reject→不落盘                  │
│         │                             │ +created_by + append LED       │
└────┬────┘                             └────────┬───────────────┬───────┘
     │ trace                           退役/失活 │  append intent │
     ▼ 指针入宿主 log（脱敏）                     ▼  的 LED        ▼
  [宿主 log]                              ┌──────────┐    ┌──────────┐
                                          │ MNG 生命 │    │ LED 账本 │
                                          │ 周期     │    │ (sidecar)│
                                          └──────────┘    └──────────┘
```

每格的行为边界 / 接口契约见 per-module 文档：[cap](cap.md) · [ref](ref.md) · [validate-store](validate-store.md) · [reflector-subagent](reflector-subagent.md)（REF 的运行载体）。

## 组件职责

- **CAP 捕获** — **唯一用 hook 的一步**：host-agnostic hook 抓每个对话回合（用户输入 + agent 输出 + tool I/O），只搬运不裁决；入口过脱敏红线；原始 trace 不自存，按指针引宿主 log；触发 = `Stop` + 递归 guard + 计数闸 + `SessionEnd` flush，per-session 计数器。详见 [cap](cap.md)。
- **REF 反思** — **注入最近 ~10 轮对话（config 可调，非完整 context）**，在 episode 边界 **compare-first**：先读现有 skill 的描述索引（**global+project 两层并集**）、锁定重叠候选，再决定**改 / 并 / 新建 / 删**，**经 stage_skill 发成 intent**（不落盘）：body（create / overwrite）或 delta（patch）+ `reason / evidence`（自带 LED）。**create 还判落 project / global 层**（默认 project、global 严）；动作 / 层由 promoter 现算或解析、模型不另声明（create 的 `level` 例外）。不产真空"雏形"。详见 [ref](ref.md)，运行载体见 [reflector-subagent](reflector-subagent.md)。
- **校验·存储** — **admission 模型、live 唯一确定性写者**：读 intent → **内存成型**（create / overwrite=body；patch=读 live + 应用 delta；delete=移除）→ **内存校验**（确定性 linter，不调 LLM：`skills_guard` 安全 + #416 结构 + LED 有 + 内容完整 + global repo-agnostic）→ **pass：写 temp 同目录 + `os.replace` 原子 rename 进对应层**（create→intent 的 `level`、update→promoter 定位层）+ `created_by:agent` sidecar + append intent 自带 LED；**reject：什么都没写**。**validate-before-ANY-write**（校验前任何盘都不落，无 staging tree / 无版本史）；去重不在闸：REF compare-first + MNG。详见 [validate-store](validate-store.md)。
- **MNG 生命周期** — 确定性，按 provenance 两层各圈成员、只归档不删除、惰性 `SessionStart` 现算。判据 = **调用率**（被调次数 / 创建以来 API 请求数，分子分母均由 CAP 逐回合捕获供给；repo 用本层、global 用全局）而非墙钟（非常驻宿主下时间冤枉「没机会被用」者）。**缓刑护新**（样本未达成熟阈值不淘汰、不占上限）+ **容量竞争**（成熟池超上限按率归档最低者）；状态 probation→active→archived（archived 移目录出召回）。**MNG 不注册自有 hook**，curation 由 CAP 会话边界 dispatch（守「hooks 仅 CAP」）；config 旋钮分层、遵守度留后；退役补记 LED。详见 [mng](mng.md)。
- **LED 账本** — 每符号 sidecar 的 append-only 账本。条目**随 intent 自带**（stage_skill 必填 `reason / evidence`），**promoter pass 那刻**才 append 进真 LED（reject 不入账）；MNG 退役亦补记。记动作 + 理由 + 证据（脱敏切片 + 宿主 log 指针）+ **watermark**（已反思到哪）；不进 skill 体以护召回。

## 全局不变量

- **纯叠加、零侵入原生**：增强只经 hooks（仅 CAP）+ 写 skill 目录，不改宿主 skill 注册 / 读取链路。
- **REF 不自审（author ≠ validator）**：生成与过闸分离——过闸是确定性 linter + `skills_guard`（独立于作者），不是 REF；质量 / 去重的独立验证交 MNG 动态兜底，v1 不设上线前第二个模型。
- **精确 / 安全 → 确定性，判断 → LLM**：安全（`skills_guard`）/ 提交 / 撞名走确定性；重复 / 正确 / 价值 / 漏更新交 LLM。
- **validate-before-ANY-write**：校验通过前**任何盘都不落**；模型只经 stage_skill 发 intent，promoter 内存成型 + 内存校验、pass 才 temp + 原子 rename（强于 Hermes write-first，无 staging tree）。
- **模型只 propose、land 确定性 promoter 独占**：reflector 只有 `Read/Grep/stage_skill`、无 validate/commit 工具 → 结构上 land 不了、跳不过闸；promoter 由编排（CAP hook → spawn → promoter）无条件调，崩则 durable 队列补处理、fail-safe。

> 各模块行为与本地理由见 per-module（[ref](ref.md) · [validate-store](validate-store.md) · [reflector-subagent](reflector-subagent.md) · [mng](mng.md)）；被比较过的取舍（write-first / draft-first / 用不用 git…）归 [decisions/](../decisions/index.md)。

## 待解

- **动态验证（遵守度）—— 本项目论点的未建核心**：符号应靠遵守度随用随验挣存活；机制未建。当前以 MNG 的调用率 + 容量竞争兜底，遵守度留后（详见 [mng](mng.md)）。

> 各模块自身的待解见对应 per-module 文档（dry-run / episode 边界 / `--agent` 继承…）；离线"兜底重放"地位未定，留 [decisions/](../decisions/index.md)。

---

provenance（idea ↔ 元素**多对多**，非一一对应；下面只标主要所凭）：

- **横切**：[dynamic-validation-lifecycle](../ideas/dynamic-validation-lifecycle.md)（理念，贯穿）、[additive-over-native-skill](../ideas/additive-over-native-skill.md)（零侵入 + 最小权限，约束 REF/校验·存储/MNG）、[skill-recall-low-degrades-with-n](../ideas/skill-recall-low-degrades-with-n.md)（召回，驱动描述卫生 + 去重 + MNG 删冗余）、[lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)（成员资格 + 自产标注）、[record-scenarios-for-eval](../ideas/record-scenarios-for-eval.md)（LED + watermark）。
- **各元素主要所凭**：CAP←[trace-based-pattern-extraction](../ideas/trace-based-pattern-extraction.md)；REF←[episode-boundary-reflection](../ideas/episode-boundary-reflection.md)；校验·存储←skill-recall · [precipitate-storage-layer](../ideas/precipitate-storage-layer.md)（`.claude/skills`）· [adherence-driven-curate](../ideas/adherence-driven-curate.md)（consolidation）；MNG←[adherence-driven-curate](../ideas/adherence-driven-curate.md)。（[hook-forced-injection](../ideas/hook-forced-injection.md) 的「强制注入」**未采纳**——forward path 选原生 skill，hooks 仅 CAP 用。）

设计元素是 idea 的**装配**，按管道职责切分；每格的行为边界 / 接口契约 / 验收落在其单独的 per-module 文档；idea 只是上游素材，不等于设计。
