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


def _seed_cat(roots, name, category, use=0, view=0, lvl="project"):
    root = roots[lvl]
    cat = f"category: {category}\n" if category else ""
    skill_store.write_body(lvl, name, f"---\nname: {name}\ndescription: use when {name}\n{cat}---\nb", root)
    s = sidecar.create(lvl, name, 0, root)
    s.update(use=use, view=view)
    sidecar.write(lvl, name, s, root)


def test_category_rates_partition_the_layer_totals(tmp_path):
    # the per-category split must add back up to the layer number, or one of the two is lying
    roots = _roots(tmp_path)
    _requests(roots, "project", 50)
    _seed_cat(roots, "hot-a", "ops", use=10, view=2)
    _seed_cat(roots, "hot-b", "ops", use=5, view=1)
    _seed_cat(roots, "cold", "docs", use=0, view=3)
    m = metrics.collect(roots)["project"]
    by = m["by_category"]
    assert sum(c["use_total"] for c in by.values()) == m["use_total"]
    assert sum(c["view_total"] for c in by.values()) == m["view_total"]
    assert sum(c["live_symbols"] for c in by.values()) == m["live_symbols"]


def test_category_recall_rate_shares_the_layer_denominator(tmp_path):
    roots = _roots(tmp_path)
    _requests(roots, "project", 40)
    _seed_cat(roots, "a", "ops", use=8)
    _seed_cat(roots, "b", "docs", use=2)
    by = metrics.collect(roots)["project"]["by_category"]
    assert by["ops"]["recall_rate"] > by["docs"]["recall_rate"]  # same denominator, more uses
    assert by["ops"]["recall_rate"] == 8 / 40


def test_uncategorized_symbols_report_under_general(tmp_path):
    roots = _roots(tmp_path)
    _requests(roots, "project", 10)
    _seed_cat(roots, "unfiled", None, use=1)
    assert metrics.collect(roots)["project"]["by_category"]["general"]["use_total"] == 1


def test_dead_category_is_visible_as_zero_not_absent(tmp_path):
    # the point of the dimension: "which category is entirely dead" must be readable, and a dead
    # category that vanished from the report would read as "no such category"
    roots = _roots(tmp_path)
    _requests(roots, "project", 20)
    _seed_cat(roots, "alive", "ops", use=4)
    _seed_cat(roots, "dead", "legacy", use=0, view=0)
    by = metrics.collect(roots)["project"]["by_category"]
    assert by["legacy"]["recall_rate"] == 0 and by["legacy"]["live_symbols"] == 1


def test_category_dimension_does_not_reach_lifecycle(tmp_path):
    # observation only: lifecycle.evaluate has no category input, so no metric can become a quota
    import inspect

    from autoharness.lib import lifecycle
    assert "category" not in inspect.signature(lifecycle.evaluate).parameters
    assert "category" not in inspect.getsource(lifecycle)
