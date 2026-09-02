from autoharness.lib import sidecar


def test_create_and_read_roundtrip(tmp_path):
    sidecar.create("project", "foo", anchor=7, root=tmp_path)
    d = sidecar.read("project", "foo", tmp_path)
    assert d["created_by"] == "agent"
    assert d["anchor"] == 7
    assert d["use"] == 0


def test_bump_use_increments(tmp_path):
    sidecar.create("project", "foo", anchor=0, root=tmp_path)
    assert sidecar.bump_use("project", "foo", tmp_path) == 1
    assert sidecar.bump_use("project", "foo", tmp_path) == 2
    assert sidecar.read("project", "foo", tmp_path)["use"] == 2


def test_is_agent_created(tmp_path):
    assert not sidecar.is_agent_created("project", "foo", tmp_path)  # no sidecar -> False (only touch self-produced)
    sidecar.create("project", "foo", 0, tmp_path)
    assert sidecar.is_agent_created("project", "foo", tmp_path)


def test_missing_sidecar_reads_empty(tmp_path):
    assert sidecar.read("project", "nope", tmp_path) == {}


def test_anchor_preserved_across_call_bumps(tmp_path):
    sidecar.create("global", "g", anchor=42, root=tmp_path)
    sidecar.bump_use("global", "g", tmp_path)
    assert sidecar.read("global", "g", tmp_path)["anchor"] == 42


# --- three-way counters (hermes-parity Phase 10, direction C) ---

def test_create_has_three_counters(tmp_path):
    d = sidecar.create("project", "tri", 0, tmp_path)
    assert d["use"] == 0 and d["view"] == 0 and d["patch"] == 0


def test_bumps_are_independent(tmp_path):
    sidecar.create("project", "tri", 0, tmp_path)
    assert sidecar.bump_use("project", "tri", tmp_path) == 1
    assert sidecar.bump_view("project", "tri", tmp_path) == 1
    assert sidecar.bump_view("project", "tri", tmp_path) == 2
    assert sidecar.bump_patch("project", "tri", tmp_path) == 1
    d = sidecar.read("project", "tri", tmp_path)
    assert (d["use"], d["view"], d["patch"]) == (1, 2, 1)


def test_legacy_calls_migrates_to_use_once(tmp_path):
    sidecar.write("project", "old", {"created_by": "agent", "calls": 7, "anchor": 0}, tmp_path)
    d = sidecar.read("project", "old", tmp_path)
    assert d.get("use", 0) + d.get("calls", 0) == 7  # no double count either way
    sidecar.bump_use("project", "old", tmp_path)
    d = sidecar.read("project", "old", tmp_path)
    assert d["use"] == 8 and "calls" not in d  # migrated once, idempotent


def test_reuse_after_patch_marked_on_first_use(tmp_path):
    sidecar.create("project", "p", 0, tmp_path)
    sidecar.bump_use("project", "p", tmp_path)
    sidecar.bump_patch("project", "p", tmp_path)
    d = sidecar.read("project", "p", tmp_path)
    assert d.get("reused_gen", 0) < d["patch"]  # not yet reused since the patch
    sidecar.bump_use("project", "p", tmp_path)
    d = sidecar.read("project", "p", tmp_path)
    assert d["reused_gen"] == d["patch"]  # first use after patch marks the reuse generation
