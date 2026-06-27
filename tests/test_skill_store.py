import pytest

from autoharness.lib import layer, skill_store


def test_write_read_roundtrip(tmp_path):
    skill_store.write_body("project", "foo", "# Foo\nbody", tmp_path)
    assert skill_store.read_body("project", "foo", tmp_path) == "# Foo\nbody"
    assert skill_store.exists("project", "foo", tmp_path)


def test_read_missing_is_none(tmp_path):
    assert skill_store.read_body("project", "x", tmp_path) is None
    assert not skill_store.exists("project", "x", tmp_path)


def test_find_two_layer_and_ambiguity(tmp_path):
    g, p = tmp_path / "g", tmp_path / "p"
    roots = {"global": g, "project": p}
    skill_store.write_body("project", "foo", "b", p)
    assert skill_store.find("foo", roots) == "project"
    assert skill_store.find("missing", roots) is None
    skill_store.write_body("global", "foo", "b", g)
    with pytest.raises(ValueError):  # same name across both layers → error to disambiguate
        skill_store.find("foo", roots)


def test_apply_delta_unique_only():
    assert skill_store.apply_delta("a X b", "X", "Y") == "a Y b"
    with pytest.raises(ValueError):
        skill_store.apply_delta("ab", "Z", "Y")          # old_string not found
    with pytest.raises(ValueError):
        skill_store.apply_delta("X and X", "X", "Y")      # old_string ambiguous (multiple matches)


def test_remove(tmp_path):
    skill_store.write_body("project", "foo", "b", tmp_path)
    skill_store.remove("project", "foo", tmp_path)
    assert not skill_store.exists("project", "foo", tmp_path)


def test_archive_restore_roundtrip_preserves_sidecar(tmp_path):
    from autoharness.lib import sidecar
    skill_store.write_body("project", "foo", "real", tmp_path)
    sidecar.create("project", "foo", anchor=3, root=tmp_path)
    skill_store.archive("project", "foo", tmp_path)
    assert not skill_store.exists("project", "foo", tmp_path)         # out of live tree
    assert (layer.archive_dir("project", tmp_path) / "foo").exists()  # parked in archive
    skill_store.restore("project", "foo", tmp_path)
    assert skill_store.read_body("project", "foo", tmp_path) == "real"    # reversible
    assert sidecar.read("project", "foo", tmp_path)["anchor"] == 3        # sidecar rode along
    assert not (layer.archive_dir("project", tmp_path) / "foo").exists()  # archive slot cleared


def test_sweep_orphans_removes_tmp_keeps_live(tmp_path):
    sdir = layer.symbol_dir("project", "foo", tmp_path)
    sdir.mkdir(parents=True)
    (sdir / "SKILL.md.dead.tmp").write_text("half-written")
    skill_store.write_body("project", "foo", "real", tmp_path)
    removed = skill_store.sweep_orphans("project", tmp_path)
    assert removed and all(str(r).endswith(".tmp") for r in removed)
    assert skill_store.read_body("project", "foo", tmp_path) == "real"  # live file intact
    assert list(layer.skills_dir("project", tmp_path).rglob("*.tmp")) == []
