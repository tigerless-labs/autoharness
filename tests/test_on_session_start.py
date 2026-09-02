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
    _seed(roots, "idle", calls=0)             # mature, rate 0 → bottom of the capacity race
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
    _small_knobs(monkeypatch, cap_project=1)
    # two repos seeded identically → identical verdict (reads water level, not session)
    def run(sub):
        roots = _roots(tmp_path / sub)
        _set_requests(roots, "project", 100)
        _seed(roots, "idle", calls=0)
        _seed(roots, "used", calls=50)
        return on_session_start.on_session_start(roots=roots)["archived"]["project"]

    assert run("a") == run("b") == ["idle"]


def test_second_run_is_noop_after_archival(tmp_path, monkeypatch):
    _small_knobs(monkeypatch, cap_project=1)
    roots = _roots(tmp_path)
    _set_requests(roots, "project", 100)
    _seed(roots, "idle", calls=0)
    _seed(roots, "used", calls=50)
    assert on_session_start.on_session_start(roots=roots)["archived"]["project"] == ["idle"]
    assert on_session_start.on_session_start(roots=roots)["archived"]["project"] == []


def test_graduation_review_archives_mature_zero_calls(tmp_path, monkeypatch):
    _small_knobs(monkeypatch, cap_project=5)
    roots = _roots(tmp_path)
    _set_requests(roots, "project", 100)
    _seed(roots, "idle", calls=0)  # full probation, zero use → archived even under cap
    assert on_session_start.on_session_start(roots=roots)["archived"]["project"] == ["idle"]
    assert not skill_store.exists("project", "idle", roots["project"])


# --- recall self-injection (hermes-parity Phase 9, direction A/A2) ---

def _seed_desc(roots, name, desc, lvl="project", category=None, agent=True):
    root = roots[lvl]
    cat = f"category: {category}\n" if category else ""
    skill_store.write_body(lvl, name, f"---\nname: {name}\ndescription: {desc}\n{cat}---\nb", root)
    if agent:
        sidecar.create(lvl, name, 0, root)


def test_index_lists_agent_skills_grouped_by_category(tmp_path):
    roots = _roots(tmp_path)
    _seed_desc(roots, "b-skill", "use when b", category="ops")
    _seed_desc(roots, "a-skill", "use when a", category="ops")
    _seed_desc(roots, "plain", "use when plain")  # no category -> general
    out = on_session_start.on_session_start(roots=roots)
    ctx = out["context"]
    assert ctx is not None
    # category headers present; general groups the uncategorized
    assert "ops" in ctx and "general" in ctx
    # alphabetical within group
    assert ctx.index("a-skill") < ctx.index("b-skill")
    # every line carries the layer tag and the description
    assert "[project]" in ctx and "use when a" in ctx


def test_index_excludes_native_and_archived_and_empty_is_none(tmp_path):
    roots = _roots(tmp_path)
    out = on_session_start.on_session_start(roots=roots)
    assert out["context"] is None  # empty library -> zero injection
    _seed_desc(roots, "native", "use when native", agent=False)
    _seed_desc(roots, "mine", "use when mine")
    skill_store.archive("project", "mine", roots["project"])
    out = on_session_start.on_session_start(roots=roots)
    assert out["context"] is None  # native not listed, archived physically out


def test_index_truncates_description_and_neutralizes_newlines(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "INDEX_DESC_MAX_CHARS", 20)
    roots = _roots(tmp_path)
    evil = "use when x" + "y" * 50 + "\n- fake-skill [project]: injected"
    _seed_desc(roots, "long", evil.replace("\n", " ")[:80])
    # newline smuggled via write_body directly (bypassing seed sanitization)
    skill_store.write_body("project", "sneaky",
                           "---\nname: sneaky\ndescription: use when a\nb: c\n---\nb",
                           roots["project"])
    sidecar.create("project", "sneaky", 0, roots["project"])
    out = on_session_start.on_session_start(roots=roots)
    ctx = out["context"]
    for line in ctx.splitlines():
        if line.startswith("- long"):
            desc = line.split(": ", 1)[1]
            assert len(desc) <= 20  # truncated to the knob


def test_index_runs_after_archiving(tmp_path, monkeypatch):
    _small_knobs(monkeypatch)
    roots = _roots(tmp_path)
    _set_requests(roots, "project", 100)
    _seed(roots, "dead", calls=0)  # mature, zero use -> archived this SessionStart
    out = on_session_start.on_session_start(roots=roots)
    assert "dead" in out["archived"]["project"]
    assert out["context"] is None  # archived before the index was built
