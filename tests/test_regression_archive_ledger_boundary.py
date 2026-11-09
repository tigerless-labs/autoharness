import pytest

from autoharness.lib import ledger


def test_archived_ledger_cannot_read_outside_archive(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / ledger.FILENAME).write_text('{"private": true}\n')
    for name in ["../../outside", str(outside), "bad/name", ".."]:
        with pytest.raises(ValueError):
            ledger.read("project", name, tmp_path, archived=True)


def test_valid_archived_ledger_still_reads(tmp_path):
    archive = tmp_path / "skills" / ".archive" / "safe"
    archive.mkdir(parents=True)
    (archive / ledger.FILENAME).write_text('{"reason": "retired"}\n')
    assert ledger.read("project", "safe", tmp_path, archived=True) == [
        {"reason": "retired"}
    ]
