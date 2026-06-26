"""端到端 live 占位：真宿主装 plugin 跑全闭环，归 experiments/E7_plugin_e2e。

确定性接缝（dispatch 路由 / MCP serve / 清单 / spawn 跨进程）已在 CI 覆盖
（test_dispatch / test_stage_skill / test_manifests / test_spawn）。本桩只标记 live 边界、
指向手测 runbook；`pytest -m "not live"` 排除它，故不堵 CI。
"""
import pytest

pytestmark = pytest.mark.live


def test_plugin_end_to_end_on_real_host():
    pytest.skip(
        "Manual/live: follow experiments/E7_plugin_e2e/runbook.md on a real Claude Code host "
        "(isolated HOME + shrunk AUTOHARNESS_* knobs), then record results in results.md."
    )
