from pathlib import Path

from autoharness.lib import intent_queue, ledger, sidecar, skill_store


def test_storage_readers_ignore_legacy_platform_default_encoding(tmp_path, monkeypatch):
    text = "你好 café"
    skill_store.write_body("project", "skill", text, tmp_path)
    sidecar.write("project", "skill", {"note": text}, tmp_path)
    ledger.append("project", "skill", {"reason": text}, tmp_path)
    intent_queue.append("run", {"body": text}, tmp_path)
    original = Path.read_text

    def legacy_read(self, encoding=None, errors=None):
        return original(self, encoding=encoding or "cp1252", errors=errors)

    monkeypatch.setattr(Path, "read_text", legacy_read)
    assert skill_store.read_body("project", "skill", tmp_path) == text
    assert sidecar.read("project", "skill", tmp_path) == {"note": text}
    assert ledger.read("project", "skill", tmp_path) == [{"reason": text}]
    assert intent_queue.read("run", tmp_path) == [{"body": text}]
