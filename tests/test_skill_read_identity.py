from autoharness import config
from autoharness.hook import on_skill_call
from autoharness.lib import sidecar, skill_store


def test_exact_read_disambiguates_same_named_global_and_project_skills(
    tmp_path, monkeypatch
):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    roots = {"global": tmp_path / "g", "project": tmp_path / "p"}
    for lyr in roots:
        skill_store.write_body(lyr, "same", "body", roots[lyr])
        sidecar.create(lyr, "same", 0, roots[lyr])
    event = {
        "tool_input": {"file_path": str(roots["project"] / "skills/same/SKILL.md")}
    }
    result = on_skill_call.on_skill_read(event, roots=roots)
    assert result["counted"] and result["level"] == "project"
    assert sidecar.read("project", "same", roots["project"])["view"] == 1
    assert sidecar.read("global", "same", roots["global"])["view"] == 0


def test_relative_read_uses_host_cwd_and_does_not_claim_native_skill(
    tmp_path, monkeypatch
):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    roots = {"global": tmp_path / "g", "project": tmp_path / "project/.claude"}
    skill_store.write_body("project", "mine", "body", roots["project"])
    sidecar.create("project", "mine", 0, roots["project"])
    event = {
        "cwd": str(tmp_path / "project"),
        "tool_input": {"file_path": ".claude/skills/mine/SKILL.md"},
    }
    assert on_skill_call.on_skill_read(event, roots=roots)["counted"]
    skill_store.write_body("global", "native", "body", roots["global"])
    sidecar.create("global", "native", 0, roots["global"])
    skill_store.write_body("project", "native", "body", roots["project"])
    event["tool_input"]["file_path"] = ".claude/skills/native/SKILL.md"
    assert not on_skill_call.on_skill_read(event, roots=roots)["counted"]
    assert sidecar.read("global", "native", roots["global"])["view"] == 0
