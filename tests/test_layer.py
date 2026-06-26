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
    # state区与 live skills 不相交（计数/队列绝不入 live skills 树）
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
