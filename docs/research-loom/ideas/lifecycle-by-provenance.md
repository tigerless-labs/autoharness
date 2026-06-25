---
id: lifecycle-by-provenance
type: idea
status: 候选
---
# 按 provenance 划生命周期成员；默认机器自产入池、其余 opt-in（含「只维护」模式）

> 合并原「维护脱离自积累」一卡。status 候选，待复核。

**主张**：生命周期（失活 / 淘汰 / 自动沉降）的**成员资格按 provenance 默认划线**——

- **默认入池 = 机器自学的经验**（本系统自产符号）：用得好上浮、被矛盾下沉、长期没用自动退役。
- **默认在池外 = 其他来源**（用户手写、外部下载、Hub 装、原生 skill）：不被自动沉降，守住 [不影响原生 skill 功能](additive-over-native-skill.md)。
- **可显式 opt-in**：把指定的其他来源符号纳入生命周期，享受自动沉降。正向加入，非默认卷入。

划线的轴是**系统内生的所有权标记（机器自产 vs 外来）**，非外部清单或文件位置。**权限 = 所有权标记 + 默认保守**：只有带「机器自产」标记者默认进自动维护；即便入池，默认只失活 / 可逆归档，不默认改写 / 合并（fail-safe、deny-by-default）。唯一硬要求是引擎能判定「是否自产」；承载形式（内联标记 vs 单独登记表）未定。

## 「只维护」模式：维护可脱离自积累单独成立

生命周期机制对符号**来源不可知**——管机器自产，同样能管用户手写的原生 skill。于是「**自积累**（自动生成新符号）」与「**维护**（去重 / 退役 / 纠偏已有符号）」**可解耦交付**。存在一类用户：不想要自动生成，却苦于手写 skill 越攒越多、互相打架、过期——给他们「**只维护、不生成**」模式，是更低门槛入口，也扩大可服务人群（对商业 / 谨慎用户尤其友好：无新增行为 = 低风险、易合规，是 audit / gate / rollback 治理卖点的轻量入口）。

落地形态（opt-in 未来档，暂不纳首版）：能判定「是否自产」即够、不需独立池子；对外来 skill 的任何失活 / 改写必须**可回滚**；改动生效前留**用户验证窗口**（仅留接口位，机制待设计）；默认只失活 / 归类。

## 论据 / 出处

[Hermes](../sources/github/nousresearch-hermes-agent.md) 代码实证正反两面：它**也**只对 `skill_manage create` 的自产物跑失活（30/90 天），其余默认豁免——方向对；但其保护轴是**外部渠道清单（bundled/hub）+ 手动 `pin`**，且明说「manually authored skills are not inferred from filesystem location」，对「即兴 `/learn`、手动 clone」有识别盲区。教训：(1) 默认按 provenance 分池对；(2) 所有权不能只靠外部清单 / 人手 pin——autoharness 改做**系统内生标记 + 显式 opt-in 加入**。[滚动 curate](adherence-driven-curate.md) 借的 Hermes curator 骨架作用于「一个符号集合」、不要求集合是机器生成的——这正是「只维护」模式可独立成立的机制依据。

## 待解 / 边界

- provenance 判定的**承载形式未定**（内联标记 vs 登记表）。
- opt-in 的**粒度与可逆性**（逐符号 / 按目录 / 按来源；能否对称 opt-out）。
- 更强动作（改写 / 合并）对外来符号的阈值与收紧程度。
- 「只维护」与「维护 + 自积累」是两个 SKU 还是一个开关，待定。
- 与 [不影响原生 skill 功能](additive-over-native-skill.md) 的张力：维护原生 skill 必然要改写 / 退役它——化解靠显式授权 + 可回滚 + 验证窗口（其中用户验证机制仍待设计）。

## 关联

是 [滚动 curate](adherence-driven-curate.md) 的成员资格规则（谁进这条流）；受 [不影响原生 skill 功能](additive-over-native-skill.md) 约束（默认不碰外来）。装配进 [design/](../design/index.md) 的 MNG（兼产品定位）。
