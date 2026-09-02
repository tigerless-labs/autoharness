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


def test_pretooluse_reaches_dispatch_for_every_tool_exactly_once():
    # direction H: the activity numerator is *every* main-session tool call, so a tool-name
    # matcher would silently drop Bash/Grep/Task from the count. One catch-all group, not
    # several: two matching groups would invoke dispatch twice for the same call and double-bump.
    pre = _load("hooks/hooks.json")["hooks"]["PreToolUse"]
    assert len(pre) == 1
    assert pre[0].get("matcher", "*") in ("*", "")


def test_pretooluse_backstops_reflector_writes():
    # S1/S3: the reflector write deny is a top-level PreToolUse backstop (not agent frontmatter),
    # so the catch-all group must be the one carrying dispatch — routing is dispatch's job.
    pre = _load("hooks/hooks.json")["hooks"]["PreToolUse"]
    assert any("autoharness.hook.dispatch" in hook["command"]
               for group in pre for hook in group["hooks"])


def test_mcp_registers_existing_stage_skill():
    m = _load(".mcp.json")["mcpServers"]["stage_skill"]
    assert "autoharness.stage_skill.server" in m["args"]
    assert (ROOT / "src/autoharness/stage_skill/server.py").exists()


def test_mcp_ships_only_this_plugin_servers():
    # a plugin-root .mcp.json is installed into every user's session: a dev-only server left
    # here would launch third-party code on their machine. Least privilege at the ship boundary.
    assert set(_load(".mcp.json")["mcpServers"]) == {"stage_skill"}


def test_marketplace_lists_this_plugin():
    mk = _load(".claude-plugin/marketplace.json")
    assert "autoharness" in [p["name"] for p in mk["plugins"]]


def test_agents_reflector_present():
    assert (ROOT / "agents/reflector.md").exists()


def test_agents_curator_present():
    assert (ROOT / "agents/curator.md").exists()  # the periodic consolidation pass agent


def test_learn_skill_ships_with_the_plugin():
    # user-invocable entry (direction B1): must live in the plugin's skills/ tree to be offered
    assert (ROOT / "skills" / "learn" / "SKILL.md").is_file()
