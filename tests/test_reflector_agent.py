from pathlib import Path

from autoharness.lib import validate

AGENT = Path(__file__).resolve().parents[1] / "agents" / "reflector.md"


def test_reflector_frontmatter_present():
    fm = validate._frontmatter(AGENT.read_text())
    assert fm is not None and fm.get("name") and fm.get("model")


def test_reflector_tools_are_least_privilege():
    fm = validate._frontmatter(AGENT.read_text())
    tools = fm["tools"]
    for allowed in ("Read", "Grep", "Glob"):
        assert allowed in tools
    # Plugin MCP tools are named mcp__plugin_<plugin>_<server>__<tool> — a bare "stage_skill"
    # (or even mcp__stage_skill__stage_skill) is silently dropped, leaving the reflector with
    # no write face at all. The live e2e caught exactly this.
    assert "mcp__plugin_autoharness_stage_skill__stage_skill" in tools
    for forbidden in ("Write", "Edit", "Bash"):
        assert forbidden not in tools  # author≠validator: no path to live skill tree


def test_reflector_body_binds_emit_only():
    body = AGENT.read_text()
    assert "stage_skill" in body  # the only sanctioned write face


def test_reflector_body_teaches_folder_skill():
    body = AGENT.read_text()
    for token in ("files", "scripts/", "templates/", "references/", "class-level"):
        assert token in body


def test_reflector_prompt_has_no_authoring_gates():
    body = AGENT.read_text().lower()
    for gate in ("at most one", "do not capture", "only valid if"):
        assert gate not in body


def test_reflector_prompt_encourages_generation():
    body = AGENT.read_text().lower()
    assert "one intent per" in body
    assert body.index("patch") < body.index("`create`")


def test_reflector_create_is_umbrella_first():
    body = AGENT.read_text().lower()
    assert "umbrella" in body  # new skills are born as a category, not a session artifact
    assert body.index("umbrella") > body.index("`create`")  # the emphasis lands on the create rung


def test_reflector_can_consolidate_existing_overlap():
    body = AGENT.read_text().lower()
    # (a) global consolidation on the cheap: the reflector may fold two PRE-EXISTING overlapping
    # skills together — not only capture the current episode's lesson. Distinctive to this rule
    # is that it deletes a *redundant existing* skill the episode never touched.
    assert "redundant" in body
    assert "delete" in body
