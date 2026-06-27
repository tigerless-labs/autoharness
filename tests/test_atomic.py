from autoharness.lib import atomic


def test_write_replaces_and_leaves_no_tmp(tmp_path):
    p = tmp_path / "sub" / "f.json"
    atomic.write_text(p, "hello")
    assert p.read_text() == "hello"
    atomic.write_text(p, "world")
    assert p.read_text() == "world"
    # after a successful atomic rename, no leftover .tmp in the dir (no half-state/orphan)
    assert list(p.parent.glob("*.tmp")) == []


def test_write_bytes_roundtrip(tmp_path):
    p = tmp_path / "b.bin"
    atomic.write_bytes(p, b"\x00\x01\x02")
    assert p.read_bytes() == b"\x00\x01\x02"
