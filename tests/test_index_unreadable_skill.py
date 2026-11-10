from autoharness.hook import on_session_start, spawn
from autoharness.lib import sidecar, skill_store


def test_bad_utf8_skill_does_not_disable_other_recall_or_reflection_entries(
    tmp_path, caplog
):
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    for name in ("healthy", "damaged"):
        skill_store.write_body(
            "project",
            name,
            f"---\nname: {name}\ndescription: useful-{name}\n---\nbody",
            roots["project"],
        )
        sidecar.create("project", name, 0, roots["project"])
    damaged = roots["project"] / "skills/damaged/SKILL.md"
    damaged.write_bytes(b"\xff\xfe invalid UTF-8")
    before = damaged.read_bytes()
    recall = on_session_start.on_session_start(roots=roots)["context"]
    assert "useful-healthy" in recall
    assert "damaged" not in recall
    assert "useful-healthy" in spawn.description_index(roots)
    assert "skipping unreadable skill" in caplog.text
    assert damaged.read_bytes() == before
