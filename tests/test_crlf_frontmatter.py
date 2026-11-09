from autoharness.lib import validate

BODY = "---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n"
INTENT = {
    "action": "create",
    "name": "foo",
    "level": "project",
    "reason": "observed reuse",
    "evidence": "fixture evidence",
}


def test_crlf_skill_has_the_same_frontmatter_and_verdict_as_lf():
    assert validate._frontmatter(BODY.replace("\n", "\r\n")) == validate._frontmatter(
        BODY
    )
    assert validate.validate(INTENT, BODY.replace("\n", "\r\n"))["ok"]
    assert validate._body_lines(BODY.replace("\n", "\r\n")) == validate._body_lines(
        BODY
    )
