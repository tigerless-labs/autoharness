import pytest

from autoharness.lib import validate

BODY = "---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n"
INTENT = {
    "action": "create",
    "name": "foo",
    "level": "project",
    "reason": "observed reuse",
    "evidence": "fixture evidence",
}


@pytest.mark.parametrize("files", [["scripts/helper.sh"], "scripts/helper.sh", 7])
def test_non_map_files_are_rejected_without_a_crash(files):
    verdict = validate.validate({**INTENT, "files": files}, BODY)
    assert not verdict["ok"] and any(
        family == "files" for family, _ in verdict["findings"]
    )


@pytest.mark.parametrize("body", [7, ["rule"], {"text": "rule"}])
def test_non_string_body_is_rejected_without_a_crash(body):
    verdict = validate.validate(INTENT, body)
    assert not verdict["ok"] and any(
        family == "structure" for family, _ in verdict["findings"]
    )


@pytest.mark.parametrize("field", ["reason", "evidence"])
def test_non_string_led_is_rejected_without_a_crash(field):
    verdict = validate.validate({**INTENT, field: 7}, BODY)
    assert not verdict["ok"] and any(
        family == "led" for family, _ in verdict["findings"]
    )
