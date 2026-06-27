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
