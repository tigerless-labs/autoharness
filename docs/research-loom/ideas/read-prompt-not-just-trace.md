---
id: read-prompt-not-just-trace
type: idea
status: 候选
---
# 直接读用户输入与 agent 输出，而非从 tool 执行反推

> user 提出，对 [ECC](../sources/github/affaan-m-ecc.md) 抓取口的修正，status 候选，待复核。

**主张**:候选符号的信号源应当**直接取用户输入 + agent 输出**,而不是只盯 tool 的执行 I/O。意图、纠正、决策本就在「用户原话」和「agent 的回应」里**明文存在**;tool trace 只是意图的**下游投影**,从重编辑/回退去反推「用户纠正了什么」是有损且间接的。读上游(prompt + 输出)保真度更高:纠正是字面的,工作流意图是说出来的,无需猜。

## 论据 / 出处

[ECC](../sources/github/affaan-m-ecc.md) 代码级审计的硬伤正在此:它只抓 `Pre/PostToolUse` 的 tool I/O,**读不到用户 prompt**,所以「用户纠正」类模式全靠从工具序列反推——盲区大、不可复现。把抓取口从「tool 执行」上移到「对话回合(用户输入 / agent 输出)」即可直接消除这层反推。

**代价要正视**:用户原话含 PII / 密钥的概率远高于 tool I/O(ECC 已对 tool 输出做 secret-scrub),所以这条路**对入口脱敏的要求更硬**——读 prompt 必须先过红线过滤(见 CLAUDE.md 安全条款)。tool trace 仍保留**「实际发生了什么」的执行地真**价值,二者宜**互补**(prompt 给意图,trace 给落地),而非单取其一。

## 关联

直接修正 [历史 trace 提模式](trace-based-pattern-extraction.md) 借来的 ECC 抓取前端(那张卡已点出「读不到用户原话」是硬伤,本卡把它升为正面设计)。更高保真的「被遵守/被矛盾」判定也回馈 [滚动 curate](adherence-driven-curate.md)——对照能直接看 agent 输出有没有照 instinct 做。
