from autoharness import config
from autoharness.hook import on_session_start
from autoharness.lib import layer, sidecar, skill_store


def _roots(base):
    return {"global": base / "g", "project": base / "p"}


def _seed(roots, name, calls, anchor=0, lvl="project"):
    root = roots[lvl]
    skill_store.write_body(lvl, name, f"---\nname: {name}\ndescription: d\n---\nb", root)
    s = sidecar.create(lvl, name, anchor, root)
    s["calls"] = calls
    sidecar.write(lvl, name, s, root)


def _set_requests(roots, lvl, n):
    p = layer.state_dir(lvl, roots[lvl]) / "requests"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(n))


def _small_knobs(monkeypatch, cap_project=5):
    monkeypatch.setattr(config, "MATURITY_THRESHOLD", {"global": 10, "project": 10})
    monkeypatch.setattr(config, "CAPACITY", {"global": 5, "project": cap_project})


def test_archives_idle_and_overflow_keeps_strong_and_probation(tmp_path, monkeypatch):
    _small_knobs(monkeypatch, cap_project=1)
    roots = _roots(tmp_path)
    _set_requests(roots, "project", 100)
    _seed(roots, "idle", calls=0)             # mature, zero calls → graduation audit
    _seed(roots, "weak", calls=5)             # rate .05, loses capacity race
    _seed(roots, "strong", calls=80)          # rate .8, top of pool → kept
    _seed(roots, "baby", calls=1, anchor=95)  # denom 5 < 10 → probation → survives

    out = on_session_start.on_session_start(roots=roots)
    assert set(out["archived"]["project"]) == {"idle", "weak"}
    assert set(out["archived"]) == {"global", "project"}  # both layers processed
    for gone in ("idle", "weak"):
        assert not skill_store.exists("project", gone, roots["project"])
    assert skill_store.exists("project", "strong", roots["project"])
    assert skill_store.exists("project", "baby", roots["project"])
    skill_store.restore("project", "weak", roots["project"])  # reversible
    assert skill_store.exists("project", "weak", roots["project"])


def test_native_skill_never_archived(tmp_path, monkeypatch):
    _small_knobs(monkeypatch)
    roots = _roots(tmp_path)
    _set_requests(roots, "project", 100)
    # native: no sidecar, zero usage, mature window — must stay (not a member)
    skill_store.write_body("project", "native",
                           "---\nname: native\ndescription: d\n---\nb", roots["project"])
    out = on_session_start.on_session_start(roots=roots)
    assert "native" not in out["archived"]["project"]
    assert skill_store.exists("project", "native", roots["project"])


def test_verdict_reads_accumulated_state_same_across_repos(tmp_path, monkeypatch):
    _small_knobs(monkeypatch)
    # two repos seeded identically → identical verdict (reads water level, not session)
    def run(sub):
        roots = _roots(tmp_path / sub)
        _set_requests(roots, "project", 100)
        _seed(roots, "idle", calls=0)
        _seed(roots, "used", calls=50)
        return on_session_start.on_session_start(roots=roots)["archived"]["project"]

    assert run("a") == run("b") == ["idle"]


def test_second_run_is_noop_after_archival(tmp_path, monkeypatch):
    _small_knobs(monkeypatch)
    roots = _roots(tmp_path)
    _set_requests(roots, "project", 100)
    _seed(roots, "idle", calls=0)
    assert on_session_start.on_session_start(roots=roots)["archived"]["project"] == ["idle"]
    assert on_session_start.on_session_start(roots=roots)["archived"]["project"] == []
