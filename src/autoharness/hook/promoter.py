"""promoter: the sole deterministic writer of the host skill tree (admission gate, ★security chokepoint).

Read the intent (the proposal the reflector sent via stage_skill) → shape the final full text in memory →
validate the six classes in memory → only on pass write atomically to disk (validate-before-ANY-write).
The model only proposes, never touches disk; landing and validation all happen here. Modeled on K8s
validating admission (validate in-flight, persist only on allow) + POSIX atomic-write.

- Shaping: create/update = intent body; patch = read live + apply delta; delete = None (removal).
- Layer resolution: create takes the intent `level`; update/patch/delete go through skill_store.find
  (same name across layers errors, missing is rejected).
- Validation: reuse lib.validate's six classes, fed {**intent, level: resolved layer} (the global gate
  applies to update too).
- Land (after pass): land intent subfiles first (paths re-gated; every landing parent resolved and
  escape-checked BEFORE any write — a pre-planted symlink rejects with zero writes) → materialize the
  evidence slice into references/evidence-<hash>.md (redacted again at this egress, content-addressed →
  idempotent; the model never names or writes it) → write SKILL.md last (atomic replace = the commit
  point: recall only reads SKILL.md, so a reader never sees it point at an unlanded subfile) → create
  stamps the sidecar created_by:agent → append the intent's own LED with evidence as the slice's
  relative path. delete = materialize evidence + LED retirement + archive move-out (whole-dir
  os.replace carries the slices along). Reject = zero writes, no stamp, no ledger.
- Drain: read queue → promote one by one → clear at the end (at-least-once + atomic land = effectively
  exactly-once); on startup sweep orphan .tmp. On a crash, unprocessed intents stay in the durable queue
  and are retried next time; in the extreme of never running → zero land (fail-safe).

ponytail: a single synchronous process already satisfies "serial single writer"; cross-process locking see mng open. LED watermark / create anchor get true values from CAP (Phase 4); v1 anchor uses the arg default 0. Whole-run clear, the tiny crash window (between land and clear) may re-append the LED — per-item idempotent watermark pending the intent-queue granularity being finalized (validate-store open).
"""
import hashlib

from autoharness.lib import (
    atomic,
    intent_queue,
    layer,
    ledger,
    redact,
    sidecar,
    skill_store,
    validate,
)

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


def _led(intent, evidence_ref):
    return {"action": intent.get("action"),
            "reason": intent.get("reason"),
            "evidence": evidence_ref}


def _materialize_evidence(level, name, evidence, root):
    text = redact.redact(evidence)
    rel = f"references/evidence-{hashlib.sha256(text.encode('utf-8')).hexdigest()[:8]}.md"
    p = layer.subfile_path(level, name, rel, root)
    if not p.exists():
        atomic.write_text(p, text)
    return rel


def _land_files(level, name, files, root):
    if not files:
        return
    sdir = layer.symbol_dir(level, name, root).resolve()
    paths = {rel: layer.subfile_path(level, name, rel, root) for rel in sorted(files)}
    for rel, p in paths.items():
        if not p.resolve().is_relative_to(sdir):
            raise ValueError(f"subfile escapes the skill dir: {rel}")
    for rel, p in paths.items():
        atomic.write_text(p, files[rel])


def _land(action, intent, body, level, name, root, anchor):
    if action == "delete":
        evidence_ref = _materialize_evidence(level, name, intent.get("evidence"), root)
        ledger.append(level, name, _led(intent, evidence_ref), root)
        skill_store.archive(level, name, root)
        return
    _land_files(level, name, intent.get("files"), root)
    evidence_ref = _materialize_evidence(level, name, intent.get("evidence"), root)
    skill_store.write_body(level, name, body, root)
    if action == "create":
        sidecar.create(level, name, anchor, root)
    ledger.append(level, name, _led(intent, evidence_ref), root)


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

    try:
        _land(action, intent, body, level, name, root, anchor)
    except ValueError as exc:
        return _reject(action, level, [("landing", str(exc))])
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
