"""promoter：宿主 skill 树的唯一确定性写者（admission 闸，★安全 chokepoint）。

读 intent（reflector 经 stage_skill 发来的提案）→ 内存成型最终全文 → 内存校验六类 →
pass 才原子落盘（validate-before-ANY-write）。模型只 propose、碰不到盘；land 与校验全在这。
仿 K8s validating admission（校验 in-flight、allow 才 persist）+ POSIX atomic-write。

- 成型：create/update=intent body；patch=read live + apply delta；delete=None（移除）。
- 层解析：create 取 intent `level`；update/patch/delete 走 skill_store.find（同名跨层报错、缺失拒）。
- 校验：复用 lib.validate 六类，喂 {**intent, level:解析层}（global 闸对 update 亦生效）。
- land（pass 后）：写 SKILL.md（原子）→ create 盖 sidecar created_by:agent → append intent 自带 LED；
  delete=LED 退役 + archive 移走。reject=零落盘、不打标、不入账。
- drain：read 队列 → 逐条 promote → 末尾 clear（at-least-once + 原子 land = 实际 exactly-once）；
  启动 sweep 孤儿 .tmp。崩溃下未处理 intent 留 durable 队列、下次补；极端没跑 → 零 land（fail-safe）。

ponytail: 单进程同步即满足「串行单写者」；跨进程锁见 mng 待解。LED watermark / create anchor
由 CAP（Phase 4）供真值，v1 anchor 走入参缺省 0。整 run clear，崩溃极窗（land 与 clear 之间）
可重 append LED —— 逐条幂等 watermark 待 intent 队列粒度定稿（validate-store 待解）。
"""
from autoharness.lib import intent_queue, layer, ledger, sidecar, skill_store, validate

_MODIFY = ("update", "patch", "delete")


def _reject(action, level, findings):
    return {"ok": False, "action": action, "level": level, "findings": findings}


def _resolve_level(intent, roots):
    if intent.get("action") == "create":
        return intent.get("level")
    return skill_store.find(intent.get("name"), roots)


def _shape(intent, level, root):
    action = intent.get("action")
    if action in ("create", "update"):
        body = intent.get("body")
        if body is None:
            raise ValueError(f"{action} requires body")
        return body
    if action == "patch":
        live = skill_store.read_body(level, intent.get("name"), root)
        if live is None:
            raise ValueError("patch target has no live body")
        return skill_store.apply_delta(live, intent["old_string"], intent["new_string"])
    if action == "delete":
        return None
    raise ValueError(f"unknown action: {action!r}")


def _led(intent):
    return {"action": intent.get("action"),
            "reason": intent.get("reason"),
            "evidence": intent.get("evidence")}


def _land(action, intent, body, level, name, root, anchor):
    if action == "delete":
        ledger.append(level, name, _led(intent), root)
        skill_store.archive(level, name, root)
        return
    skill_store.write_body(level, name, body, root)
    if action == "create":
        sidecar.create(level, name, anchor, root)
    ledger.append(level, name, _led(intent), root)


def promote(intent, *, roots=None, repo_name=None, anchor=0):
    roots = roots or {}
    action = intent.get("action")
    name = intent.get("name")

    try:
        level = _resolve_level(intent, roots)
    except ValueError as exc:
        return _reject(action, None, [("routing", str(exc))])
    if level not in layer.LAYERS:
        return _reject(action, level, [("routing", f"unresolved/illegal level: {level!r}")])

    root = roots.get(level)
    try:
        body = _shape(intent, level, root)
        base_dir = layer.symbol_dir(level, name, root)
    except (ValueError, KeyError) as exc:
        return _reject(action, level, [("shape", str(exc))])

    target_created = sidecar.is_agent_created(level, name, root) if action in _MODIFY else None

    verdict = validate.validate(
        {**intent, "level": level}, body,
        target_is_agent_created=target_created, repo_name=repo_name, base_dir=base_dir,
    )
    if not verdict["ok"]:
        return _reject(action, level, verdict["findings"])

    _land(action, intent, body, level, name, root, anchor)
    return {"ok": True, "action": action, "level": level, "findings": []}


def sweep(roots=None):
    roots = roots or {}
    removed = []
    for lyr in layer.LAYERS:
        removed += skill_store.sweep_orphans(lyr, roots.get(lyr))
    return removed


def drain(run_id, *, roots=None, repo_name=None, anchor=0):
    roots = roots or {}
    sweep(roots)
    proot = roots.get(layer.PROJECT)
    verdicts = [promote(i, roots=roots, repo_name=repo_name, anchor=anchor)
                for i in intent_queue.read(run_id, proot)]
    intent_queue.clear(run_id, proot)
    return verdicts
