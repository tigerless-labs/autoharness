---
id: trace-based-pattern-extraction
type: idea
status: 候选
---
# 候选来料：从对话回合捕获，而非只从 tool 执行反推

> 借 [ECC](../sources/github/affaan-m-ecc.md) 抓取前端 + user 对抓取口的修正。合并原「直接读 prompt」一卡。status 候选，待复核。

**主张**：候选符号**不依赖标注 benchmark**，直接从 agent 的运行痕迹里长出来——hook 抓取，攒到一定量后让便宜模型扫近窗，把**重复出现的模式**（用户纠正、错误→修复、固定工作流、工具偏好）蒸馏成候选；信号天然带「这事真发生过且重复」，省人工打标。但**抓取口要取对话回合（用户输入 + agent 输出），而非只盯 tool 执行 I/O**：意图、纠正、决策本就在用户原话与 agent 回应里**明文存在**；tool trace 只是意图的下游投影，从重编辑 / 回退反推「用户纠正了什么」有损且不可复现。读上游保真更高。

## 论据 / 出处

[ECC](../sources/github/affaan-m-ecc.md) 代码级审计证实其「学习」前端：`Pre/PostToolUse` hook 抓 tool I/O → 单次 Haiku 扫近窗 → 写出 3+ 次复现的模式。便宜、无标注、走套餐即可跑通——**抓取 + 一次性生成**这个前端值得借。

**但只借前端，并修一处硬伤**：ECC 只看 tool trace、**读不到用户原话**（纠正全靠从重编辑 / 回退反推），窗口截断成盲区，「模式 / 重复」全交模型 gestalt、无算法、不可复现。把抓取口从「tool 执行」上移到「对话回合」即消除反推这层。**代价**：用户原话含 PII / 密钥的概率远高于 tool I/O（ECC 已对 tool 输出 secret-scrub），故这条路**对入口脱敏要求更硬**——读 prompt 必先过红线过滤（CLAUDE.md 安全条款）。tool trace 仍保留「实际发生了什么」的执行地真，二者**互补**（prompt 给意图、trace 给落地），非单取其一。

所以痕迹只能当**候选来料**，不能当准入裁决。

## 关联

是准入裁决的上游来源（捕获供料 → 把关）；提取出的「固定工作流」即潜在**顺序边**。捕获的对话回合交 [episode 边界反思](episode-boundary-reflection.md) 整段蒸馏；更高保真的「被遵守 / 被矛盾」对照也回馈 [滚动 curate](adherence-driven-curate.md)。装配进 [design/](../design/index.md) 的 CAP。
