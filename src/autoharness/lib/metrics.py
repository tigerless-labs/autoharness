"""Runtime health metrics: read-only derivation over the accounts the pipeline already keeps.

metrics.md: continuously answers "is this maintenance layer doing anything" — the lara post-mortem's
core failure was that `calls≈0` went unnoticed for weeks because nothing reported it. Distinct from
eval (offline judgement with a budget): this is per-session bookkeeping already on disk, re-read.

**Observation only.** Nothing here may feed a lifecycle decision — eviction stays with mng's rate
criterion. Changing a metric definition must never change system behavior.

Derived, never newly instrumented: sidecar three-way counters (use/view/patch + reused_gen), the
per-symbol append-only ledger (delete entries carry absorbed_into), the run-level verdict accounts
promoter writes, and the layer request counters. Death causes partition the archived set: absorbed
(merged into an umbrella) / pruned (deliberate retirement) / lifecycle (MNG rate or capacity, which
leaves no delete entry) — merging is shape convergence, not mortality, so the split is load-bearing.

ponytail: window granularity is cumulative-since-creation (mirrors the rate denominator); a rolling
window is deferred with the same open question in mng.md.
"""
import json

from autoharness.lib import layer, ledger, sidecar, skill_store


def _live_symbols(lyr, root):
    skills = layer.skills_dir(lyr, root)
    if not skills.exists():
        return []
    return [p.parent.name for p in skills.glob(f"*/{skill_store.SKILL_FILE}")
            if sidecar.is_agent_created(lyr, p.parent.name, root)]


def _archived_symbols(lyr, root):
    adir = layer.archive_dir(lyr, root)
    if not adir.exists():
        return []
    return [p.parent.name for p in adir.glob(f"*/{skill_store.SKILL_FILE}")]


def _deaths(lyr, root, names):
    causes = {"absorbed": 0, "pruned": 0, "lifecycle": 0}
    for name in names:
        entries = ledger.read(lyr, name, root, archived=True)
        deletes = [e for e in entries if e.get("action") == "delete"]
        if not deletes:
            causes["lifecycle"] += 1  # archived by MNG: rate/capacity, no intent behind it
        elif deletes[-1].get("absorbed_into"):
            causes["absorbed"] += 1
        else:
            causes["pruned"] += 1
    return causes


def _funnel(lyr, root):
    runs = layer.state_dir(lyr, root) / "runs"
    proposed = landed = 0
    families = {}
    if runs.exists():
        for path in runs.glob("*.json"):
            try:
                run = json.loads(path.read_text())
            except (ValueError, OSError):
                continue  # a corrupt account never breaks reporting
            for v in run.get("verdicts", []):
                proposed += 1
                if v.get("ok"):
                    landed += 1
                for family in v.get("findings", []):
                    families[family] = families.get(family, 0) + 1
    return {"proposed": proposed, "landed": landed, "rejected": proposed - landed}, families


def _layer_metrics(lyr, root):
    from autoharness.lib import counters

    live = _live_symbols(lyr, root)
    cards = [sidecar.read(lyr, name, root) for name in live]
    use_total = sum(c.get("use", 0) for c in cards)
    view_total = sum(c.get("view", 0) for c in cards)
    requests = counters.request_count(lyr, root)
    patched = [c for c in cards if c.get("patch", 0) > 0]
    reused = [c for c in patched if c.get("reused_gen", 0) >= c.get("patch", 0)]
    archived = _archived_symbols(lyr, root)
    funnel, families = _funnel(lyr, root)
    return {
        "live_symbols": len(live),
        "use_total": use_total,
        "view_total": view_total,
        "requests": requests,
        "recall_rate": use_total / requests if requests else 0,
        "view_rate": view_total / requests if requests else 0,
        "used_symbol_share": sum(1 for c in cards if c.get("use", 0)) / len(cards) if cards else 0,
        "archived_total": len(archived),
        "deaths": _deaths(lyr, root, archived),
        "funnel": funnel,
        "reject_families": families,
        "reuse_after_patch": len(reused) / len(patched) if patched else 0,
    }


def collect(roots=None):
    roots = roots or {}
    return {lyr: _layer_metrics(lyr, roots.get(lyr)) for lyr in layer.LAYERS}
