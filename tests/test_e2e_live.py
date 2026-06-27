"""End-to-end live placeholder: install the plugin on a real host and run the full loop, under experiments/E7_plugin_e2e.

The deterministic seams (dispatch routing / MCP serve / manifests / cross-process spawn) are already covered in CI
(test_dispatch / test_stage_skill / test_manifests / test_spawn). This stub only marks the live boundary and
points to the manual-test runbook; `pytest -m "not live"` excludes it, so it does not block CI.
"""
import pytest

pytestmark = pytest.mark.live


def test_plugin_end_to_end_on_real_host():
    pytest.skip(
        "Manual/live: follow experiments/E7_plugin_e2e/runbook.md on a real Claude Code host "
        "(isolated HOME + shrunk AUTOHARNESS_* knobs), then record results in results.md."
    )
