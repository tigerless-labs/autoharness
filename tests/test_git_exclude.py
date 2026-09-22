import subprocess

import pytest

from autoharness.lib import git_exclude


def _git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          cwd=cwd, check=True, capture_output=True, text=True).stdout


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    (root / ".agents" / "skills" / "handwritten").mkdir(parents=True)
    (root / ".agents" / "skills" / "handwritten" / "SKILL.md").write_text("x")
    _git(tmp_path, "init", "-q", str(root))
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "init")
    return root


def _land(root, name):
    skill = root / ".agents" / "skills" / name
    skill.mkdir()
    (skill / "SKILL.md").write_text("x")


def test_prefixed_skills_disappear_from_status_hand_written_ones_do_not(repo):
    _land(repo, "ah-dates")
    assert git_exclude.ensure(repo / ".agents" / "skills", "ah-") == "/.agents/skills/ah-*"
    (repo / ".agents" / "skills" / "newly-handwritten").mkdir()
    (repo / ".agents" / "skills" / "newly-handwritten" / "SKILL.md").write_text("x")
    status = _git(repo, "status", "--porcelain", "--untracked-files=all")
    assert "ah-dates" not in status and "newly-handwritten" in status


def test_pattern_is_written_once(repo):
    _land(repo, "ah-a")
    for _ in range(3):
        git_exclude.ensure(repo / ".agents" / "skills", "ah-")
    exclude = (repo / ".git" / "info" / "exclude").read_text().splitlines()
    assert exclude.count("/.agents/skills/ah-*") == 1


def test_linked_worktrees_share_the_one_pattern(repo, tmp_path):
    _git(repo, "worktree", "add", "-q", "-b", "wt", str(tmp_path / "wt"))
    git_exclude.ensure(repo / ".agents" / "skills", "ah-")
    _land(tmp_path / "wt", "ah-b")
    assert "ah-b" not in _git(tmp_path / "wt", "status", "--porcelain", "--untracked-files=all")


def test_no_prefix_writes_nothing(repo):
    assert git_exclude.ensure(repo / ".agents" / "skills", "") is None
    assert "ah-" not in (repo / ".git" / "info" / "exclude").read_text()


def test_outside_a_repository_writes_nothing(tmp_path):
    (tmp_path / "skills").mkdir()
    assert git_exclude.ensure(tmp_path / "skills", "ah-") is None
