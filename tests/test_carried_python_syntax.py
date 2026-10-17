from autoharness.lib import validate

BODY = "---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n"
INTENT = {
    "action": "create",
    "name": "foo",
    "level": "project",
    "reason": "observed reuse",
    "evidence": "fixture evidence",
}


def test_new_carried_python_script_is_syntax_checked(tmp_path):
    body = BODY + "See `scripts/helper.py`.\n"
    verdict = validate.validate(
        {**INTENT, "files": {"scripts/helper.py": "def broken(:\n"}},
        body,
        base_dir=tmp_path,
    )
    assert any(
        family == "structure" and "syntax error" in detail
        for family, detail in verdict["findings"]
    )


def test_replacement_python_script_is_checked_instead_of_old_disk(tmp_path):
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/helper.py").write_text("def broken(:\n")
    verdict = validate.validate(
        {**INTENT, "files": {"scripts/helper.py": "print('valid')\n"}},
        BODY + "See `scripts/helper.py`.\n",
        base_dir=tmp_path,
    )
    assert verdict["ok"], verdict["findings"]
