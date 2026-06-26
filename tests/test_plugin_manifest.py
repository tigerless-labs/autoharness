import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(rel):
    return json.loads((ROOT / rel).read_text())


def test_plugin_json_has_identity():
    m = _load(".claude-plugin/plugin.json")
    assert m["name"] == "autoharness"
    assert m["version"]


def test_hooks_route_all_events_to_dispatch():
    h = _load("hooks/hooks.json")["hooks"]
    assert set(h) == {"SessionStart", "Stop", "PreToolUse", "SessionEnd"}
    for groups in h.values():
        for group in groups:
            for hook in group["hooks"]:
                assert "autoharness.hook.dispatch" in hook["command"]
    assert (ROOT / "src/autoharness/hook/dispatch.py").exists()


def test_pretooluse_scoped_to_skill():
    pre = _load("hooks/hooks.json")["hooks"]["PreToolUse"]
    assert any(group.get("matcher") == "Skill" for group in pre)


def test_pretooluse_backstops_reflector_writes():
    # S1/S3: reflector write deny is a top-level PreToolUse matcher (not agent frontmatter)
    pre = _load("hooks/hooks.json")["hooks"]["PreToolUse"]
    assert any("Write" in (group.get("matcher") or "") for group in pre)


def test_mcp_registers_existing_stage_skill():
    m = _load(".mcp.json")["mcpServers"]["stage_skill"]
    assert "autoharness.stage_skill.server" in m["args"]
    assert (ROOT / "src/autoharness/stage_skill/server.py").exists()


def test_marketplace_lists_this_plugin():
    mk = _load(".claude-plugin/marketplace.json")
    assert "autoharness" in [p["name"] for p in mk["plugins"]]


def test_agents_reflector_present():
    assert (ROOT / "agents/reflector.md").exists()
