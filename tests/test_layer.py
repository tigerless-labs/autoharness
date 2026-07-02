import pytest

from autoharness.lib import layer


def test_layers_are_the_two_known():
    assert set(layer.LAYERS) == {"global", "project"}


@pytest.mark.parametrize("lyr", layer.LAYERS)
def test_paths_nest_under_root(tmp_path, lyr):
    skills = layer.skills_dir(lyr, tmp_path)
    assert skills == tmp_path / "skills"
    assert layer.archive_dir(lyr, tmp_path) == skills / ".archive"
    assert layer.symbol_dir(lyr, "foo", tmp_path) == skills / "foo"
    assert layer.state_dir(lyr, tmp_path) == tmp_path / "autoharness"
    # state area is disjoint from live skills (counters/queues never enter the live skills tree)
    assert layer.state_dir(lyr, tmp_path) != skills
    assert layer.archive_dir(lyr, tmp_path) != layer.symbol_dir(lyr, "foo", tmp_path)


def test_default_roots_differ_between_layers():
    assert layer.default_root("global") != layer.default_root("project")


@pytest.mark.parametrize("fn", [layer.skills_dir, layer.archive_dir, layer.state_dir])
def test_unknown_layer_rejected(fn):
    with pytest.raises(ValueError):
        fn("staging", "/tmp/whatever")


@pytest.mark.parametrize("bad", ["../evil", "a/b", "a\\b", "..", ".", ".archive", ""])
def test_symbol_name_traversal_rejected(tmp_path, bad):
    with pytest.raises(ValueError):
        layer.symbol_dir("project", bad, tmp_path)


def test_valid_symbol_name_ok(tmp_path):
    assert layer.symbol_dir("project", "my_skill-2.v1", tmp_path).name == "my_skill-2.v1"


# --- subfile path gate (folder-skill) ---

@pytest.mark.parametrize("rel", ["scripts/run.sh", "references/notes.md",
                                 "templates/py/starter.py", "assets/logo.svg"])
def test_subfile_path_accepted_and_nests_under_symbol(tmp_path, rel):
    layer.check_subfile(rel)
    p = layer.subfile_path("project", "foo", rel, tmp_path)
    assert p == layer.symbol_dir("project", "foo", tmp_path) / rel


@pytest.mark.parametrize("bad", [
    "../x", "/etc/passwd", "scripts/../SKILL.md",      # traversal / absolute
    "bin/x.sh",                                         # non-whitelist top dir
    "notes.md", "SKILL.md", ".sidecar.json", ".ledger.jsonl",  # <2 segments: no top-level files
    "references/.hidden", "references//x",              # dot segment / empty segment
    "scripts/a\\b", "", None, 7,                        # backslash / empty / non-str
])
def test_subfile_gate_rejects(bad):
    with pytest.raises(ValueError):
        layer.check_subfile(bad)


def test_subfile_dirs_whitelist_is_the_four():
    assert set(layer.SUBFILE_DIRS) == {"scripts", "templates", "assets", "references"}
