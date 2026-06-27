from autoharness.lib import sidecar


def test_create_and_read_roundtrip(tmp_path):
    sidecar.create("project", "foo", anchor=7, root=tmp_path)
    d = sidecar.read("project", "foo", tmp_path)
    assert d["created_by"] == "agent"
    assert d["anchor"] == 7
    assert d["calls"] == 0


def test_bump_calls_increments(tmp_path):
    sidecar.create("project", "foo", anchor=0, root=tmp_path)
    assert sidecar.bump_calls("project", "foo", tmp_path) == 1
    assert sidecar.bump_calls("project", "foo", tmp_path) == 2
    assert sidecar.read("project", "foo", tmp_path)["calls"] == 2


def test_is_agent_created(tmp_path):
    assert not sidecar.is_agent_created("project", "foo", tmp_path)  # no sidecar -> False (only touch self-produced)
    sidecar.create("project", "foo", 0, tmp_path)
    assert sidecar.is_agent_created("project", "foo", tmp_path)


def test_missing_sidecar_reads_empty(tmp_path):
    assert sidecar.read("project", "nope", tmp_path) == {}


def test_anchor_preserved_across_call_bumps(tmp_path):
    sidecar.create("global", "g", anchor=42, root=tmp_path)
    sidecar.bump_calls("global", "g", tmp_path)
    assert sidecar.read("global", "g", tmp_path)["anchor"] == 42
