import json

import pytest

from autoharness.hook import on_session_start
from autoharness.lib import layer, sidecar, skill_store


@pytest.mark.parametrize("record", [[], None, 3, {"families": 4}, {"families": [4]}])
def test_bad_previous_run_summary_does_not_starve_skill_recall(tmp_path, record):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    skill_store.write_body(
        "project",
        "useful",
        "---\nname: useful\ndescription: healthy recall\n---\nbody",
        roots["project"],
    )
    sidecar.create("project", "useful", 0, roots["project"])
    state = layer.state_dir("project", roots["project"])
    state.mkdir(parents=True, exist_ok=True)
    (state / "last_run.json").write_text(json.dumps(record))
    result = on_session_start.on_session_start(roots=roots)
    assert "healthy recall" in result["context"]
    assert not (state / "last_run.json.consuming").exists()
