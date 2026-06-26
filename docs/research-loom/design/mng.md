---
id: mng
type: design
---
# 模块设计：MNG 生命周期（调用率定生死 + 缓刑护新 + 容量竞争）

spine 的 MNG 格。决定每个**自产符号**活多久。**确定性**,惰性判定（`SessionStart` 现算）、只归档不删除、按 provenance 圈成员。判据是**调用率**而非墙钟时间;缓刑保护新符号;容量上限只在成熟池内按率竞争淘汰。上游 provenance 见 [adherence-driven-curate](../ideas/adherence-driven-curate.md),机制对照 [Hermes](../sources/github/nousresearch-hermes-agent.md) curator（我们以率取代其时间状态机,理由见下）。

## 成员资格（按 provenance，两层各圈一份）

只管带「机器自产」标记的符号（[lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)）；用户手写 / 外来 / 原生 skill 默认在池外，守 [additive-over-native-skill](../ideas/additive-over-native-skill.md)。自产标记由 [validate-store](validate-store.md) 的 Commit 盖在 sidecar。宿主两层 skill 树（project 限本仓、global 跨项目）各圈一份成员集，分别判定。

## 活跃度 = 调用率（取代时间）

存活依据是**调用率** `rate = 被调次数 / 请求数`，不是墙钟。Claude Code 非常驻：墙钟在 agent 关着时照走、会冤枉「没机会被用」的符号；请求数只在真有交互时增长，是**机会相对**的度量、对临时宿主免疫。这正接 [dynamic-validation-lifecycle](../ideas/dynamic-validation-lifecycle.md) 的随用随验（时间是弱代理，率直接量有用度）。三层强度中 v1 吃到率，遵守度仍留后。

- **分子 = 被调次数**：在 **`PreToolUse(Skill)` handler** 那刻 +1（该 handler 与 CAP 的 handler 同挂 plugin 单一 dispatcher、**不另起 hook 注册**），计入被调符号自己的 sidecar、**不分层**（符号身份即决定其 sidecar 落哪层）。零侵入下不拥有宿主 loader、抄不了 Hermes 的 callsite 计数，改在 hook 面埋点；纯观察、不拦截、不改召回链路。
- **分母 = 创建以来的 API 请求数**（每个 turn 一次，**非人类对话次数**）：**repo 符号**用本 repo 的请求数，**global 符号**用全局所有请求数（它处处加载、机会即全部请求）。CAP 每回合给对应层的请求计数器 +1；符号 sidecar 记**创建锚**（创建时的层请求计数），分母 = 当前层计数 − 锚。

计数随 sidecar 走层，promote / archive 的 `mv <符号目录>` 把分子原子带走（不抄 Hermes 单一共享计数文件：单文件每次 mv 还得另改它，而成员封顶后逐符号读 sidecar 排序的代价可忽略）。**与 LED 分工**：LED（append-only）记增删改的理由 / 证据，计数（可变）只记数。

## 缓刑护新：样本不够不淘汰、不占上限

率在小样本下是噪声（`1/1` 与 `8/100` 不可比），刚建的符号尤其会被冤。故设缓刑：

- **分母未过成熟阈值（config）= 缓刑态**：照常 live、照常被召回，但**①不计入上限 ②不参与淘汰**。
- 分母过阈值 → **毕业**入成熟池，带可比的真率。
- **毕业即审**：满样本仍率≈0（给够机会都没被调）→ 当场归档；它得到过公平机会。

## 退役 = 成熟池内按率竞争（容量触发）

- **上限只管成熟池**（分母过阈值者）；成熟数超上限（config）→ 按率升序归档最低者，回到上限内为止。
- 淘汰竞争只在样本都达标的成熟符号间发生 → 率可比、新老皆公平：新符号只在拿够机会后以真率与同辈比，**绝不「刚建就被上限挤掉」**。
- **无固定阈值 θ、自调**：被淘汰当且仅当「你最没用 **且** 有容量压力」；死亡地板只在毕业那一刻判一次。
- 状态 **probation → active（成熟）→ archived**：成熟度只管「能否被淘汰 / 算不算上限」，**不影响召回**（缓刑与成熟都 live）。**archived = 把符号目录移出 live 树** → 原生召回扫不到 → 不再注入；靠移目录、非靠状态位，可逆（移回即复活）。

## 触发：全骑 session hook，零 daemon

**MNG 不另起 hook 注册**——它的 handler 与 CAP 的同挂 plugin 单一 dispatcher（守 spine 零侵入不变量）。非常驻宿主无后台 sweep，故全部骑 session 生命周期：分子在 **`PreToolUse(Skill)` handler** +1、分母由**每回合** handler 给对应层请求计数器 +1；**重算率 + 淘汰**在 **`SessionStart` handler** 惰性现算（跑在本会话召回之前，对「到上次会话结束为止」的全部账现算）。**每会话一次、不节流**：判定是确定性便宜活（读 ≤N 个 sidecar 比一下），无须 Hermes LLM curator 那套 idle / 间隔节流。**dormancy 不积压**：关机不动分母，回来不会突然清一批。

## 两层差异

- **分子同构**：层无关，存进被调符号 sidecar。
- **分母分层**：repo = 本 repo 请求数；global = 全局请求数（全局请求计数器由每个装了 autoharness 的 repo 的 CAP 共同 +1）。
- **上限分层**：各层各设成熟阈值与容量上限（config，**两个旋钮独立可调、不写死**）；global 爆炸半径大 → 更保守。
- **判定读累积水位**：失活判定不读「本 session 看到什么」，只读 sidecar + 层计数器跨 session / 跨 repo 累积量，故任意 repo 的 `SessionStart` 触发都得同一结论。

## 决策

- 只管自产符号（provenance 圈成员），两层各圈一份、分别判定。
- 判据 = 调用率（取代墙钟时间）：非常驻宿主下墙钟冤枉「没机会被用」者，请求数是机会相对度量。
- 分子 = hook 埋点的被调次数，存被调符号 sidecar、层无关；分母 = 创建以来 API 请求数（repo 本层 / global 全局），sidecar 记创建锚。
- 缓刑护新：分母未过成熟阈值则 live 但不淘汰、不占上限；过阈值毕业、率≈0 当场归档。
- 退役 = 成熟池内超上限按率竞争归档最低者；无固定 θ、自调；状态 probation→active→archived，archived 靠移目录出召回。
- **MNG 不另起 hook 注册**：handler（`PreToolUse(Skill)` 计分子、`SessionStart` 重算淘汰）挂 plugin 单一 dispatcher、与 CAP 的 handler 并列；零 daemon、每会话一次不节流、dormancy 不积压。
- 成熟阈值与容量上限均 config、两旋钮独立、分层各设、不写死。

## 待解 / 动手前实测

- **调用捕获实测**（率分子成立的前提）：① learned skill（描述召回的）被用是否走 `Skill` 工具、触发 `PreToolUse(Skill)` handler；② 事件 payload 是否带解析后的符号身份（对得上符号）。点一个 learned skill、看 hook payload 即可验。
- **API 请求计数口径**：分母锚在「每 turn 一次的 API 请求」——确认 CAP 的 per-turn 触发与 API 请求一一对应（一个 turn 多次模型调用 / 重试是否各算一次），定义清「一次请求」。
- **global 率的「在场≫相关」偏置**：global 符号处处加载但只在部分 repo 相关（Python skill 在 Rust repo 永不被调），全局分母含无关请求会压低其率。v1 接受宽分母（global 量少、上限竞争兜底）；「分母只算曾用过它的 repo」留后。
- **global 并发写锁**：全局请求计数器 + global sidecar 被多 repo 的 hook 跨进程并发写；多 repo 的 `SessionStart` 并发归档同一 global 符号 → per-symbol + 全局计数器跨进程锁（与 [validate-store](validate-store.md) Commit 的 live 单写者锁合一把）。
- **global 覆盖盲区**：分子分母都只数装了 autoharness hook 的 repo；没装的 repo 调了 / 跑了都不计——per-repo 安装的固有 gap（Hermes 无，因它本身即 agent、永远在场）。
- **累计 vs 滚动窗口**：累计（自创建）最省；环境漂移下「曾有用、近来没用」需滚动窗口（近若干请求内的率）才能下沉，留后。
- **绝对底线规则（留后，先不实现）**：除「毕业审率≈0」外，可加一条**独立于容量**的硬底线——分母过 X **且**分子 < Y（均 config、分层）即归档，逮「给够机会仍基本没用、但还没触发容量竞争」者。是现有毕业审的推广（把率≈0 的隐含 Y=0 放成可调 Y）；落点同在 `lifecycle` + `config`，无需新埋点 / 新状态——为它专搭规则引擎属过度设计，不做。
- **成熟阈值 / 上限标定**：config 默认值待经验标定（`experiments/`）。

provenance：[adherence-driven-curate](../ideas/adherence-driven-curate.md)（生命周期骨架 + 容量 consolidation + 遵守度留后）、[lifecycle-by-provenance](../ideas/lifecycle-by-provenance.md)（自产圈成员）、[skill-recall-low-degrades-with-n](../ideas/skill-recall-low-degrades-with-n.md)（容量封顶护召回）、[record-scenarios-for-eval](../ideas/record-scenarios-for-eval.md)（sidecar 计数 / LED 分工）、[dynamic-validation-lifecycle](../ideas/dynamic-validation-lifecycle.md)（率取代时间的随用随验、遵守度留后）；机制对照 [Hermes](../sources/github/nousresearch-hermes-agent.md)（`active→stale→archived` 时间状态机 + last_used 计数 + capacity consolidation；我们以率 + 缓刑 + 容量竞争取代其墙钟判据，时间冤枉非常驻宿主）。
