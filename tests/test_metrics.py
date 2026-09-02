"""Runtime metrics (Phase 13): read-only derivation over sidecars / ledgers / run accounts /
layer counters. Observation only — nothing here may feed a lifecycle decision.

Assertions are relational (ratios reconcile, death causes partition, ordering holds), never
hardcoded magic numbers: the knobs are placeholders under calibration.
"""
import json

from autoharness.lib import layer, ledger, metrics, sidecar, skill_store


def _roots(tmp_path):
    return {"global": tmp_path / "g", "project": tmp_path / "p"}


def _seed(roots, name, use=0, view=0, patch=0, reused=0, lvl="project"):
    root = roots[lvl]
    skill_store.write_body(lvl, name, f"---\nname: {name}\ndescription: use when {name}\n---\nb", root)
    s = sidecar.create(lvl, name, 0, root)
    s.update(use=use, view=view, patch=patch, reused_gen=reused)
    sidecar.write(lvl, name, s, root)


def _requests(roots, lvl, n):
    p = layer.state_dir(lvl, roots[lvl]) / "requests"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(n))


def test_recall_and_view_rates_reconcile_with_counters(tmp_path):
    roots = _roots(tmp_path)
    _requests(roots, "project", 100)
    _seed(roots, "a", use=3, view=1)
    _seed(roots, "b", use=0, view=2)
    m = metrics.collect(roots)["project"]
    assert m["use_total"] == 3 and m["view_total"] == 3
    assert m["recall_rate"] == 3 / 100          # library-level: uses per layer request
    assert m["used_symbol_share"] == 1 / 2      # one of two symbols saw a use
    assert m["recall_rate"] <= 1.0


def test_death_causes_partition_the_archived(tmp_path):
    roots = _roots(tmp_path)
    _requests(roots, "project", 10)
    for name, entry in (("merged", {"action": "delete", "reason": "r", "evidence": "e",
                                    "absorbed_into": "umbrella"}),
                        ("pruned", {"action": "delete", "reason": "r", "evidence": "e"})):
        _seed(roots, name)
        ledger.append("project", name, entry, roots["project"])
        skill_store.archive("project", name, roots["project"])
    _seed(roots, "evicted")  # archived by MNG: no delete entry in its ledger
    skill_store.archive("project", "evicted", roots["project"])
    m = metrics.collect(roots)["project"]
    d = m["deaths"]
    assert d["absorbed"] == 1 and d["pruned"] == 1 and d["lifecycle"] == 1
    assert sum(d.values()) == m["archived_total"]  # causes partition the archived set exactly


def test_funnel_and_reuse_signals(tmp_path):
    roots = _roots(tmp_path)
    _requests(roots, "project", 10)
    _seed(roots, "improved", use=2, patch=1, reused=1)   # used after being patched
    _seed(roots, "stale_patch", use=1, patch=2, reused=1)  # patched again, not re-used since
    state = layer.state_dir("project", roots["project"]) / "runs"
    state.mkdir(parents=True, exist_ok=True)
    (state / "r1.json").write_text(json.dumps({"run_id": "r1", "verdicts": [
        {"ok": True, "findings": []}, {"ok": False, "findings": ["altitude"]},
        {"ok": False, "findings": ["trigger"]}]}))
    m = metrics.collect(roots)["project"]
    assert m["funnel"] == {"proposed": 3, "landed": 1, "rejected": 2}
    assert m["reject_families"]["altitude"] == 1 and m["reject_families"]["trigger"] == 1
    assert m["reuse_after_patch"] == 1 / 2  # one of two patched symbols was re-used since


def test_empty_library_is_safe_and_zeroed(tmp_path):
    m = metrics.collect(_roots(tmp_path))["project"]
    assert m["recall_rate"] == 0 and m["funnel"]["proposed"] == 0
    assert m["deaths"] == {"absorbed": 0, "pruned": 0, "lifecycle": 0}


def test_metrics_never_mutate_anything(tmp_path):
    roots = _roots(tmp_path)
    _requests(roots, "project", 5)
    _seed(roots, "a", use=1)
    before = sidecar.read("project", "a", roots["project"])
    metrics.collect(roots)
    assert sidecar.read("project", "a", roots["project"]) == before  # observation only
