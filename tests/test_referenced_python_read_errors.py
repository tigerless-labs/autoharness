from autoharness.lib import validate

BODY = "---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n"
INTENT = {
    "action": "create",
    "name": "foo",
    "level": "project",
    "reason": "observed reuse",
    "evidence": "fixture evidence",
}


def test_non_text_python_reference_is_rejected_without_a_decoder_crash(tmp_path):
    (tmp_path / "helper.py").write_bytes(b"\xff\xfe")
    verdict = validate.validate(INTENT, BODY + "See helper.py.\n", base_dir=tmp_path)
    assert not verdict["ok"]
    assert any(
        family == "structure" and "could not be read" in detail
        for family, detail in verdict["findings"]
    )


def test_os_read_error_is_reported_as_structure(tmp_path, monkeypatch):
    from pathlib import Path

    (tmp_path / "helper.py").write_text("print('fixture')\n")
    original = Path.read_text

    def unreadable(path, *args, **kwargs):
        if path.name == "helper.py":
            raise PermissionError("fixture read denied")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", unreadable)
    verdict = validate.validate(INTENT, BODY + "See helper.py.\n", base_dir=tmp_path)
    assert any(
        family == "structure" and "could not be read" in detail
        for family, detail in verdict["findings"]
    )
