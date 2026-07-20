# AutoHarness 录屏演示 —— 完整流程 + 脚本

> 目标视频结构:安装 → 一次真实纠正被学成 skill → skill 被原地维护 → 新会话第一次就对。
> 所有命令和 prompt **照英文原样输入**;台词为中文口播稿(括号内为英文版)。
> 目录约定:`$DEMO = ~/autoharness-walkthrough-demo`,演示仓库 = `$DEMO/repo`(镜头里唯一出现的目录)。
> 本文是录屏工作稿,验证记录见 `~/autoharness-walkthrough-demo/REPRO.md`(sandbox 全流程 4/4 通过,v0.3.0)。

## 0. 环境说明(为什么这样搭)

| 层 | 位置 | 说明 |
|---|---|---|
| 项目层(出镜) | `$DEMO/repo/.claude/skills/` | skill 落盘处,和真实用户项目一模一样 |
| 用户层(不出镜) | `$DEMO/sandbox-home/.claude/` | 用 `HOME` 覆盖隔离:画面无日常插件、Step 1 可现场装、真实 `~/.claude` 零污染 |

已固化进 `sandbox-home/.claude/settings.json`(开新终端也不会丢):

```json
{
  "autoMemoryEnabled": false,
  "env": { "AUTOHARNESS_REFLECT_EVERY_N": "2" }
}
```

- `autoMemoryEnabled: false` — 关掉 Claude Code 自带 auto-memory,让效果只归因于 skill
- `AUTOHARNESS_REFLECT_EVERY_N=2` — 纠正那轮立即触发反思(默认 10,录屏等不起)

`repo/demo-env.sh` 只做一件事:`export HOME=~/autoharness-walkthrough-demo/sandbox-home`。

**铁律:每个要跑 `claude` 的终端,先 `source demo-env.sh`,再用 `echo $HOME` 确认指向 sandbox-home。**
(排练翻车均源于漏掉这步:会话跑进真实环境,真实插件在计数、auto-memory 在记笔记、反思阈值还是 10。)

## 1. 每次开录/重拍前的 RESET(不录)

```bash
cd ~/autoharness-walkthrough-demo/repo
source demo-env.sh && echo $HOME        # 必须显示 .../sandbox-home

# 清演示产物
rm -rf .claude tests
git add -A && git commit -qm "reset for retake" 2>/dev/null

# 卸插件(让 Scene 1 能现场装;报 "not found" 说明本来就干净,忽略)
claude plugin uninstall autoharness@autoharness
claude plugin marketplace remove autoharness

# 清 sandbox 会话痕迹
rm -rf ~/autoharness-walkthrough-demo/sandbox-home/.claude/projects \
       ~/autoharness-walkthrough-demo/sandbox-home/.claude/autoharness \
       ~/autoharness-walkthrough-demo/sandbox-home/.claude/skills
```

检查就绪:`ls .claude tests` 都不存在、`claude plugin list` 显示 No plugins installed。

录屏建议:OBS + Window Capture 只录 VS Code 窗口(双屏不穿帮);VS Code `Ctrl+=` 放大两级字体。用 `code ~/autoharness-walkthrough-demo/repo` 打开工作区,集成终端里先幕后 source 再开录。

## 2. 场景 1 — 零配置安装(≈1 分钟)

**输入:** `claude`,然后依次:

```
/plugin marketplace add tigerless-labs/autoharness
```
```
/plugin install autoharness@autoharness
```

**台词:** "这就是全部的安装。没有配置文件、没有 API key、没有额外服务——免费开源、MIT 协议,直接装进你已经在用的 Claude Code 插件系统。"
(EN: *"That's the entire setup. No config file, no API key, no extra service — a free, MIT-licensed plugin that lives right inside the Claude Code plugin system you already use."*)

`/exit` 退出,重新 `claude`(hooks 生效)。

## 3. 场景 2 — 看它从一次真实纠正中学习(≈4 分钟)

**Prompt 1:**

```
Add unit tests for src/slugger.py covering slugify and truncate_words. Just write the test file; do not run anything.
```

**看缺口** — 编辑器打开 `tests/test_slugger.py`:parametrize 表全是裸元组,**没有一处 `ids=`**。
(注:别指望它写 unittest 或 class 风格——这代模型默认就写 parametrize,`ids=` 缺口才是每把都稳定存在的。)

**台词:** "写得挺像样——但等测试跑挂的时候,失败输出会是一堆裸元组。我们仓库的约定是每个 parametrize 都带 ids,失败一眼读出是哪个行为挂了。这种细节,以前每开一个新会话都得重新讲。这次我只纠正一次。"
(EN: *"Looks decent — but when a test fails, the output is raw tuples. Our convention: every parametrize carries ids, so a failure reads as a behavior name. I used to re-explain this every single session. This time I correct it once."*)

**Prompt 2(纠正):**

```
One correction on our repo test conventions: every @pytest.mark.parametrize must carry ids=[...] so failure output reads as behavior names, not raw tuples; bare assert only (no unittest imports); test files under tests/ named test_<module>.py. Adjust the file you just wrote to follow this. Please remember this convention for all future test work in this repo.
```

展示改后的文件——每个表都有了 `ids=[...]`。

**台词(等 60–90 秒时说):** "重点来了。刚才那次纠正结束了一个 episode,后台的 reflector 正在把它蒸馏成一个 skill——我没敲任何命令、没做任何配置,它已经自己在跑了。"
(EN: *"Here's where AutoHarness kicks in. That correction just closed an episode, and a background reflector is distilling it into a skill — no command, no config, it's already running."*)

**展示 skill** — Explorer 打开 `.claude/skills/<新目录>/SKILL.md`(目录名模型自起)。

**台词:** "出现了。一个普通的、人类可读的 Markdown 文件,就在项目的 .claude/skills 里——不是黑盒记忆,不是模型权重。我的约定,被插件自己写了下来。"
(EN: *"There it is. A plain, readable Markdown file on disk — not hidden memory, not model weights. My convention, written down by the plugin itself."*)

再打开同目录 `references/evidence-*.md`:

**台词:** "它还把我的原话逐字存成证据——每个 skill 都能追溯到教会它的那一刻。"
(EN: *"It even kept my exact words as evidence — every skill traces back to the moment that taught it."*)

## 4. 场景 3 — 它维护 skill,而不只是写下 skill(≈3 分钟)

`/exit` 退出,重新 `claude`。把 `SKILL.md` 放分屏保持可见。

**Prompt 1:**

```
Add unit tests for src/pricing.py covering apply_discount and split_bill. Just write the test file; do not run anything.
```

**看缺口** — 打开 `tests/test_pricing.py`:错误断言写 `pytest.raises(ValueError)`,**没有 `match=`**(模型的稳定盲区)。顺手点评:ids 这次带没带?带了就是 skill 已在起效的加分镜头。

**台词:** "还差一个细节:错误路径必须用 match 钉住报错信息,不然换个报错文案测试照样绿。再纠正一次。"
(EN: *"One detail is off: error paths must pin the message with match — otherwise the test stays green when the error text changes. One more correction."*)

**Prompt 2:**

```
Good. One more repo convention to fold in: error-path cases must be asserted with pytest.raises(ValueError, match=...) — add tests for the invalid inputs of apply_discount and split_bill using that. This belongs with our ids/bare-assert conventions; remember it for all future test work here.
```

**盯分屏:** `SKILL.md` 原地长出 error-path 规则——同一个文件更新。Explorer 一个镜头:**仍然只有一个** skill 目录。

**台词:** "注意没发生的事:没有第二个 skill、没有重复文件。新规则被折叠进已有的那个。长期不用的 skill 会被自动淘汰;你手写的 skill 有标记保护——AutoHarness 只管理它自己创作的。"
(EN: *"Notice what didn't happen: no second skill, no duplicate. The new rule folded into the existing one. Unused skills get pruned over time — and anything you wrote yourself is off-limits; AutoHarness only manages what it authored."*)

## 5. 场景 4 — 证明:同类任务第一次就对(≈2 分钟)

`/exit` 退出,重新 `claude`。

**Prompt(一句话,绝不提任何约定):**

```
Add unit tests for src/ratelimit.py covering window_key and remaining. Just write the test file; do not run anything.
```

**盯工具日志:** 它自己加载那个 skill(日志里能看到 Skill 调用),然后写文件。打开 `tests/test_ratelimit.py`。

**台词:** "全新会话、同类任务,我一个字没提约定。看:parametrize 全部自带 ids,错误断言自带 match——两次纠正它都记住了,第一次就做对。这就是回报:不再重复自己,把时间花在交付上。"
(EN: *"Brand-new session, same kind of task, and I said nothing about conventions. Every parametrize carries ids, error asserts carry match — both corrections remembered, right on the first try. That's the payoff: stop repeating yourself, ship instead."*)

**可选收尾:**

```bash
PYTHONPATH=src .venv/bin/python -m pytest tests/ -q
```

**台词:** "全绿。" (EN: *"All green."*)

## 6. 场景 5 — 有时间才录(≈30 秒)

```bash
grep -n "AUTOHARNESS_" ~/autoharness-walkthrough-demo/sandbox-home/.claude/plugins/cache/autoharness/autoharness/0.3.0/src/autoharness/config.py
```

**台词:** "反思节奏、成熟阈值、容量上限,全部环境变量可调。默认开箱即用,想要控制权时旋钮都在。"
(EN: *"Reflection cadence, maturity thresholds, capacity — all tunable via environment variables. Sensible defaults, knobs when you want them."*)

## 7. 兜底与排障

**纠正点优先级(哪个缺口真实存在就纠哪个,弧线不变):**

1. `ids=` 缺失(几乎必现)
2. `pytest.raises` 无 `match=`(几乎必现)
3. 用了 `sys.path.insert` 或 `from src.` 导入 → 纠正 "用 conftest.py 挂 src 路径"

**skill 60–90 秒后还不出现,依次查(幕后):**

```bash
echo $HOME                                   # 1. 不是 sandbox-home → 白拍了,回 RESET
pgrep -af autoharness.hook.spawn             # 2. 有进程 → 反思还在跑,再等等
ls .claude/autoharness/                      # 3. 目录不存在 → hooks 没生效(插件没装/没重启 claude)
claude plugin list                           # 4. 确认 autoharness 已安装且 enabled
```

**已知坑(排练均踩过):**

- 忘 `source demo-env.sh` → 会话跑进真实环境:真实插件计数、反思阈值 10、auto-memory 记笔记,且真实环境的 autoharness 会从排练里学出全局 skill 污染后续。发现后:删 `~/.claude/skills/<泄漏的skill>`、删 `~/.claude/projects/-home-ryan-autoharness-walkthrough-demo-repo`,回 RESET。
- "Recalled/wrote N memories" 字样 = Claude Code 自带 auto-memory 在工作,说明在真实环境(sandbox 已关掉它)。
- 每个 Scene 之间必须 `/exit` 重开 claude:episode 边界 + skill 重新加载都靠新会话。
- 第一轮产出有随机性:镜头永远对准"产出 vs 约定"的落差,发对应纠正即可,不要为赌某种错误风格反复重抽。

**录完全部清场:**

```bash
rm -rf ~/autoharness-walkthrough-demo        # sandbox + repo + traces 一锅端,真实 ~/.claude 从未被碰
```

## 8. 时长预算

| 场景 | 时长 |
|---|---|
| 1 安装 | ~1 min |
| 2 纠正→skill 诞生 | ~4 min(含 60–90s 等待,用台词填) |
| 3 原地维护 | ~3 min |
| 4 第一次就对 | ~2 min |
| 5 环境变量(可选) | ~0.5 min |
| **合计** | **~10 min** |
