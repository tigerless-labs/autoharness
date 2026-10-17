from autoharness.lib import validate

BODY = "---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n"
INTENT = {
    "action": "create",
    "name": "foo",
    "level": "project",
    "reason": "observed reuse",
    "evidence": "fixture evidence",
}


def test_carried_path_is_not_referenced_by_a_longer_filename():
    verdict = validate.validate(
        {**INTENT, "files": {"scripts/run.sh": "echo fixture\n"}},
        BODY + "See scripts/run.sh.bak.\n",
    )
    assert any(
        family == "structure" and "not referenced" in detail
        for family, detail in verdict["findings"]
    )


def test_carried_exact_path_with_markdown_punctuation_is_referenced():
    verdict = validate.validate(
        {**INTENT, "files": {"scripts/run.sh": "echo fixture\n"}},
        BODY + "Run [helper](scripts/run.sh).\n",
    )
    assert verdict["ok"], verdict["findings"]
