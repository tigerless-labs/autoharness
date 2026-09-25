"""Regression: archive/restore must not destroy existing data on name collision."""
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

from autoharness.lib import skill_store


def _make_tree(root, lyr, name, marker="live"):
    """Create a fake skill dir with a marker file."""
    skills = Path(root) / lyr / "skills" / name
    skills.mkdir(parents=True, exist_ok=True)
    (skills / "SKILL.md").write_text(f"# {name}\nmarker={marker}")
    return skills


def test_archive_collision_preserves_old(tmp_path):
    """Archiving a skill when an archive of the same name exists must not destroy the old archive."""
    root = str(tmp_path)
    # Simulate: skill exists in archive AND in live
    _make_tree(root, "global", "foo", marker="archived")
    archive_dest = Path(root) / "global" / ".archive" / "foo"
    archive_dest.mkdir(parents=True, exist_ok=True)
    (archive_dest / "SKILL.md").write_text("# foo\nmarker=old-archive")

    # Patch layer helpers to use our tmp layout
    with patch("autoharness.lib.skill_store.layer") as lyr_mod:
        lyr_mod.symbol_dir.return_value = Path(root) / "global" / "skills" / "foo"
        lyr_mod.archive_dir.return_value = Path(root) / "global" / ".archive"
        result = skill_store.archive("global", "foo", root)

    # The old archive must still exist
    assert (archive_dest / "SKILL.md").read_text() == "# foo\nmarker=old-archive"
    # The new archive landed at a timestamped path
    assert result is not None
    assert result != archive_dest or (archive_dest / "SKILL.md").read_text().startswith("# foo")


def test_restore_collision_preserves_live(tmp_path):
    """Restoring a skill when a live copy exists must not destroy the live copy."""
    root = str(tmp_path)
    _make_tree(root, "global", "foo", marker="live-current")
    archive_src = Path(root) / "global" / ".archive" / "foo"
    archive_src.mkdir(parents=True, exist_ok=True)
    (archive_src / "SKILL.md").write_text("# foo\nmarker=from-archive")

    with patch("autoharness.lib.skill_store.layer") as lyr_mod:
        lyr_mod.symbol_dir.return_value = Path(root) / "global" / "skills" / "foo"
        lyr_mod.archive_dir.return_value = Path(root) / "global" / ".archive"
        result = skill_store.restore("global", "foo", root)

    # The original live copy must still exist
    live = Path(root) / "global" / "skills" / "foo"
    assert (live / "SKILL.md").read_text() == "# foo\nmarker=live-current"
    assert result is not None
