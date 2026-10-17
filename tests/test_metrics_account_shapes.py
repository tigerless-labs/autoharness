import json

import pytest

from autoharness.lib import layer, metrics


@pytest.mark.parametrize(
    "bad",
    [
        [],
        None,
        42,
        {"verdicts": None},
        {"verdicts": "bad"},
        {"verdicts": [None, 42, []]},
        {"verdicts": [{"ok": False, "findings": [{}, ["bad"], None]}]},
    ],
)
def test_malformed_account_does_not_hide_valid_account(tmp_path, bad):
    runs = layer.state_dir("project", tmp_path) / "runs"
    runs.mkdir(parents=True)
    (runs / "bad.json").write_text(json.dumps(bad))
    (runs / "good.json").write_text(
        json.dumps({"verdicts": [{"ok": True, "findings": []}]})
    )
    funnel, families = metrics._funnel("project", tmp_path)
    assert funnel["landed"] == 1
    assert families == {}
