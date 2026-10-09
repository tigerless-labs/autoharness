import pytest

from autoharness import config
from autoharness.hook import dispatch
from autoharness.lib import counters, sidecar, skill_store


@pytest.mark.parametrize("tool", ["Write", "Edit", "MultiEdit", "NotebookEdit"])
def test_curator_event_cannot_write_without_inherited_child_env(
    tmp_path, monkeypatch, tool
):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    result = dispatch.dispatch(
        {
            "hook_event_name": "PreToolUse",
            "agent_type": config.CURATOR_AGENT,
            "tool_name": tool,
        },
        roots=roots,
    )
    assert result["deny"]


@pytest.mark.parametrize("tool", ["Read", "Skill"])
def test_curator_comparison_does_not_inflate_usage(tmp_path, monkeypatch, tool):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    skill_store.write_body("project", "owned", "body", roots["project"])
    sidecar.create("project", "owned", 0, roots["project"])
    event = {
        "hook_event_name": "PreToolUse",
        "agent_type": config.CURATOR_AGENT,
        "session_id": "child",
        "tool_name": tool,
        "tool_input": {
            "skill": "owned",
            "file_path": str(roots["project"] / "skills/owned/SKILL.md"),
        },
    }
    assert not dispatch.dispatch(event, roots=roots)["result"]["counted"]
    data = sidecar.read("project", "owned", roots["project"])
    assert data["use"] == data["view"] == 0
    assert counters.session_count("child", roots["project"]) == 0
