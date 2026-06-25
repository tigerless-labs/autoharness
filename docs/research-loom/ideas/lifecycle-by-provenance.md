---
id: lifecycle-by-provenance
type: idea
status: 候选
---
# 默认只有机器自学经验进生命周期;其他来源可 opt-in 自动沉降

**主张**:生命周期(进 [滚动 curate](adherence-driven-curate.md):衰减 / 失活 / 淘汰 / 自动沉降)的**成员资格按 provenance 默认划线**——

- **默认入池 = 机器自学的经验**(本系统自产的符号)。它本就是"基于使用信号自增长、自维护"的东西,理应有完整生命周期:用得好上浮、被矛盾下沉、长期没用自动沉降退役。
- **默认在池外 = 其他来源**(用户手写、外部下载、Hub 装、原生 skill)。不被自动沉降——这守住 [维护层只能叠加、不得改写原生](additive-over-native-skill.md):系统不擅自给人意符号判生死。
- **但用户可显式 opt-in**:把指定的其他来源符号也纳入生命周期,让它们一样享受**自动沉降**(自动 stale/降权/归档)。这是一个**正向加入**动作,不是默认就卷进去。

划线的轴必须是**系统内生的所有权标记(机器自产 vs 外来)**,而非外部清单或文件位置——见下文对照。

**权限 = 所有权标记,且默认动作保守。** 「区分生成 vs 非生成」正是这条线的**权限钥匙**:只有带「机器自产」内生标记的符号默认进自动维护。且即便入池,**默认只做失活 / 归类(可逆归档)这类退役动作,不默认改写 / 合并**;更强动作须显式 opt-in。这是 fail-safe、deny-by-default,与 [维护层只能叠加](additive-over-native-skill.md) 同源。即便沉淀物按 [precipitate-storage-layer](precipitate-storage-layer.md) 取向 B 进了 skill 层,**唯一硬要求是维护引擎能判定「是否自产」**:可判定即可——自产默认入维护,其余一律视作「其他来源」。「分池」只是抽象说法,不是独立存储;而这枚 provenance 判定**怎么承载,未定**(见待解)。

## 论据 / 出处

[Hermes](../sources/github/nousresearch-hermes-agent.md) 的代码实证给了正反两面:它**也**只对 `skill_manage create` 的自产物跑失活(30/90 天),其余默认豁免——方向对。但它的保护轴是**外部渠道清单(bundled/hub)+ 手动逐个 `pin`**,且"认不认管理"还要靠 `.usage.json` 记录、明说「manually authored skills are not inferred from filesystem location」。两个教训:(1) 默认按 provenance 分池是对的;(2) 但**所有权不能只靠外部清单/人手 pin**——那对"用户即兴 `/learn`、手动 clone"有识别盲区。autoharness 据此把成员资格做成**系统内生标记 + 显式 opt-in 加入**,而不是 Hermes 那种"默认豁免、手动 pin 退出"。

## 待解 / 边界

- provenance 判定的**承载形式未定**:随符号内联一个标记 vs 单独一张登记表(JSON/DB)。只要能判定「是否自产」即可,具体形态待 ADR / 实现定。
- opt-in 的**粒度与可逆性**:逐符号 / 按目录 / 按来源类别?纳入后能否退出(对称 opt-out)?
- 默认退役动作已定为**失活 / 归类(可逆)**;仍待定的是更强动作(改写 / 合并)对外来符号要不要进一步收紧、阈值挂钩到哪。
- **其他来源的维护现整块不做**:只标注自产、其余默认不碰即可,不需独立池子。该能力(可回滚 + 用户验证)作 opt-in **保留窗口**,见 [维护脱离自积累](maintenance-without-self-accumulation.md)。

## 关联

是 [滚动 curate](adherence-driven-curate.md) 的**成员资格规则**(谁进这条流);受 [维护层只能叠加、不得改写原生](additive-over-native-skill.md) 约束(默认不碰外来);所有权标记的内生化呼应同一张卡的教训。装配进 [design/](../design/index.md) 的 Manage 段。
