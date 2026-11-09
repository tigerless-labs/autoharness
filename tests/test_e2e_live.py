"""End-to-end live placeholder: install the plugin on a real host and run the full loop by hand.

The deterministic seams (dispatch routing / MCP serve / manifests / cross-process spawn) are already covered in CI
(test_dispatch / test_stage_skill / test_plugin_manifest / test_spawn). This stub only marks the live boundary and says
how to run it; `pytest -m "not live"` excludes it, so it does not block CI. The maintainers' full runbook lives in
their experiments/ tree, which is not part of the public release, so the skip message carries the steps itself.
"""
import pytest

pytestmark = pytest.mark.live


def test_plugin_end_to_end_on_real_host():
    pytest.skip(
        "Manual/live: on a real Claude Code host with an isolated HOME, install the plugin, shrink the "
        "AUTOHARNESS_* knobs as in README 'Walkthrough: watching it learn', work a few turns, then check "
        ".claude/autoharness/runs/ and .claude/skills/ for what landed and why."
    )
