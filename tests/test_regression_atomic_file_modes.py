import os
import stat

import pytest

from autoharness.lib import atomic


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable and permission bits")
@pytest.mark.parametrize("mode", [0o700, 0o640])
def test_replacement_preserves_existing_mode(tmp_path, mode):
    path = tmp_path / "script.py"
    path.write_text("old")
    path.chmod(mode)
    atomic.write_text(path, "new")
    assert path.read_text() == "new"
    assert stat.S_IMODE(path.stat().st_mode) == mode


def test_new_atomic_files_remain_private(tmp_path):
    path = tmp_path / "new"
    atomic.write_text(path, "private")
    if os.name != "nt":
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
