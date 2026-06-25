---
id: trace-based-pattern-extraction
type: idea
status: 候选
---
# 从历史 trace 里提模式：候选符号的无标注来源

> 借鉴 [ECC](../sources/github/affaan-m-ecc.md) 的抓取/生成前端，status 候选，待复核。

**主张**：维护层的「候选符号」可以**不依赖标注 benchmark**，直接从 agent 的历史工具调用 trace 里长出来——hook 抓取每次 tool 的输入/输出，攒到一定量后让一个便宜模型扫近窗，把**重复出现的模式**（用户纠正、错误→修复、固定工作流、工具偏好）蒸馏成候选。这是 autoharness **入料口**的现成参考：信号天然带「这事真发生过且重复」，省掉人工打标。

## 论据 / 出处

[ECC](../sources/github/affaan-m-ecc.md) 代码级审计证实其整条「学习」就是：`Pre/PostToolUse` hook 抓 tool I/O → 单次 Haiku `--print` 扫最近 500 行 → 写出 3+ 次复现的模式。便宜、无标注、走套餐即可跑通——值得借的就是这个**抓取 + 一次性生成**的前端。

**但只借前端**：ECC 的 trace 提取有硬伤，恰是 autoharness 要补的地方——只看 tool trace、**读不到用户原话**（纠正全靠从重编辑/回退反推）；窗口截断（>500 行即盲区）；「模式/重复/冲突」全交给模型 gestalt，**无算法定义、不可复现**。所以 trace 只能当**候选来源**，不能当准入裁决。

## 关联

是准入裁决的上游来源（trace 供料 → 把关）。提取出的「固定工作流」模式即潜在的**顺序边**，与 DAG 边蒸馏同源。
