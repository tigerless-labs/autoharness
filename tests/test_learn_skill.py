"""The user-invocable learn skill (Phase 12, direction B1): Hermes /learn equivalent — the live
agent distills on demand through the SAME proposal chain (stage_skill -> promoter), guards undropped."""
from pathlib import Path

from autoharness.lib import validate

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "learn" / "SKILL.md"


def test_learn_skill_exists_and_passes_own_gate():
    body = SKILL.read_text()
    v = validate.validate({"action": "create", "name": "learn", "level": "project",
                           "reason": "r", "evidence": "e"}, body)
    assert v["ok"], v["findings"]  # our own linter: trigger cue, altitude, safety, completeness


def test_learn_skill_routes_through_stage_skill_not_writes():
    body = SKILL.read_text()
    assert "stage_skill" in body
    for forbidden in ("Write(", "Edit("):
        assert forbidden not in body
