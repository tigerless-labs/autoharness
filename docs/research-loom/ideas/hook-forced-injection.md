---
id: hook-forced-injection
type: idea
status: 候选
---
# 要可靠生效的规则，走 hook 强制注入，别靠 skill 的概率触发

> 源于 ECC 实测机制，status 候选，待 user 升 `采纳` 或改 `否决`。

**主张**：规则的「载体」是决定其执行可靠度的一等变量。当一条规则**必须每次生效**时，应做成 **hook 强制注入**（`SessionStart` / `UserPromptSubmit`，其 stdout 即被当作注入上下文，确定性 **100%**），而非依赖 skill 的 **description 概率触发**（由模型判断相关性，约 **50–80%**）。由此维护层多出一维职责：按「要求的可靠度」为每条规则**选/修载体**（hook 强制注入 / 常驻上下文 / description-skill），并标出「本该常驻却被写成概率 skill」的载体错配。

## 论据 / 出处

[ECC](../sources/github/affaan-m-ecc.md) 实测此分层：观察与注入都走 hook —— `SessionStart`/`UserPromptSubmit` 把 project-scoped instinct 注入上下文（字符封顶 `ECC_SESSION_START_MAX_CHARS`≈8000，可关、可调档），**100% fire**；维护者明言「skills 概率触发 ~50–80%，hooks 100%」，故把高可靠规则全部路由到 hook 注入的 instinct，只把「偶尔相关」留给 description-skill。注入目的是**用（forward path）**而非优化——但「被遵守 / 被无视」会产出 adherence 证据，回喂观察 hook 做 curate（confidence decay）。

未定细节：项目内是 top-N-by-confidence 还是全量到封顶、`UserPromptSubmit` 是否按当前 prompt 再筛 —— 需读 ECC `scripts/hooks/`。

## 关联

采纳前提是 [维护层只能叠加，不得改写原生 skill 体验](additive-over-native-skill.md)——hook 通道必须在原生之外另开，零侵入 skill 的新增与读取。与 [结构化把关，不要 held-out 分数](structural-gate-no-oracle.md) 同属「维护层主张」。尚未装配进设计（候选去向：维护层的「载体选择 / vehicle-fit 检查」设计元素）。其上层延伸——在 hook 里跑 SkillDAG 式图召回、force-inject 依赖完整 bundle，让「边」在运行时变现而非仅供维护——为另一条待提 idea。
