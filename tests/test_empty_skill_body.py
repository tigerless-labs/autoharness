from autoharness.lib import validate

BODY = "---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n"
INTENT = {
    "action": "create",
    "name": "foo",
    "level": "project",
    "reason": "observed reuse",
    "evidence": "fixture evidence",
}


def test_frontmatter_only_is_not_a_complete_authored_skill():
    frontmatter = BODY[: BODY.index("Use strftime.")]
    for action in ["create", "update", "patch"]:
        verdict = validate.validate(
            {**INTENT, "action": action},
            frontmatter + "\n\n",
            target_is_agent_created=True,
        )
        assert any(
            family == "completeness" and "empty" in detail
            for family, detail in verdict["findings"]
        )


def test_nonempty_rule_and_retirement_remain_valid():
    assert validate.validate(INTENT, BODY)["ok"]
    assert validate.validate(
        {**INTENT, "action": "delete"}, None, target_is_agent_created=True
    )["ok"]
