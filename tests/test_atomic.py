from autoharness.lib import atomic


def test_write_replaces_and_leaves_no_tmp(tmp_path):
    p = tmp_path / "sub" / "f.json"
    atomic.write_text(p, "hello")
    assert p.read_text() == "hello"
    atomic.write_text(p, "world")
    assert p.read_text() == "world"
    # 原子 rename 成功后同目录无残留 .tmp（半态/孤儿不存在）
    assert list(p.parent.glob("*.tmp")) == []


def test_write_bytes_roundtrip(tmp_path):
    p = tmp_path / "b.bin"
    atomic.write_bytes(p, b"\x00\x01\x02")
    assert p.read_bytes() == b"\x00\x01\x02"
