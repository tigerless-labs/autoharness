from pathlib import Path

from autoharness.lib import validate

AGENT = Path(__file__).resolve().parents[1] / "agents" / "curator.md"


def test_curator_frontmatter_present():
    fm = validate._frontmatter(AGENT.read_text())
    assert fm is not None and fm.get("name") and fm.get("model")


def test_curator_tools_are_least_privilege():
    fm = validate._frontmatter(AGENT.read_text())
    tools = fm["tools"]
    for allowed in ("Read", "Grep", "Glob"):
        assert allowed in tools
    # same emit-only write face as the reflector — propose intents, never touch the live tree
    assert "mcp__plugin_autoharness_stage_skill__stage_skill" in tools
    for forbidden in ("Write", "Edit", "Bash"):
        assert forbidden not in tools


def test_curator_ports_umbrella_levers():
    body = AGENT.read_text().lower()
    for lever in ("umbrella", "class-level", "prefix", "references/", "templates/", "scripts/"):
        assert lever in body


def test_curator_teaches_three_ways_to_consolidate():
    body = AGENT.read_text().lower()
    assert "existing umbrella" in body   # (a) merge into an already-broad member
    assert "new umbrella" in body        # (b) create a fresh umbrella
    assert "demote" in body              # (c) demote narrow detail into support subfiles


def test_curator_delete_is_archive_not_destruction():
    body = AGENT.read_text().lower()
    assert "archive" in body
    assert "recoverable" in body  # delete stages an archive move-out, never a hard delete


def test_curator_only_touches_agent_created():
    body = AGENT.read_text().lower()
    assert "created_by:agent" in body or "agent-created" in body  # native/user skills are out of pool


def test_curator_is_iterative():
    body = AGENT.read_text().lower()
    assert "iterate" in body or "next umbrella" in body


def test_curator_judges_by_maintainer_bar_not_pairwise():
    body = AGENT.read_text().lower()
    assert "maintainer" in body  # "would a maintainer write N skills or one with N subsections?"
