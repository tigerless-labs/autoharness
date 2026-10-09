import json

import pytest

from autoharness.hook import spawn
from autoharness.lib import counters, layer


@pytest.mark.parametrize("curate", [False, True])
def test_missing_executable_is_recorded_without_real_child(tmp_path, curate):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    spec = tmp_path / "format.md"
    spec.write_text("test format")

    def fail(argv, env, payload):
        raise FileNotFoundError("missing-claude-test")

    with pytest.raises(FileNotFoundError):
        if curate:
            spawn.run_curator(
                "launch-failure", roots=roots, spec_path=spec, spawn_fn=fail
            )
        else:
            spawn.run(
                "window", "launch-failure", roots=roots, spec_path=spec, spawn_fn=fail
            )
    account = layer.state_dir("project", roots["project"]) / "runs/launch-failure.json"
    assert account.exists()
    record = json.loads(account.read_text())
    assert record["spawn_error"]["returncode"] is None
    assert "FileNotFoundError" in record["spawn_error"]["stderr_tail"]
    assert counters.session_offset("safe", roots["project"]) == 0
