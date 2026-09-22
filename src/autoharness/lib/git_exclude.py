"""Keeps prefixed skill directories out of git with one pattern in the repository's shared info/exclude.

A skill tree inside a working tree would otherwise show every agent-authored skill as untracked.
With a name prefix the whole library is one pattern, written once to `<git-common-dir>/info/exclude`
(local to the clone, never committed, shared by every linked worktree) the first time a skill lands
there. Hand-written skills stay visible to git. No prefix, no repository, or a skill tree outside
the working tree: nothing is written. Any git failure is swallowed — landing never depends on it.
"""
import subprocess
from pathlib import Path


def pattern(skills_dir, prefix):
    if not prefix:
        return None
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--show-toplevel", "--git-common-dir"],
            cwd=skills_dir, capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    lines = proc.stdout.splitlines()
    if proc.returncode != 0 or len(lines) < 2:
        return None
    try:
        rel = Path(skills_dir).resolve().relative_to(Path(lines[0]).resolve())
    except ValueError:
        return None
    return f"/{rel.as_posix()}/{prefix}*", Path(lines[1]) / "info" / "exclude"


def ensure(skills_dir, prefix):
    found = pattern(skills_dir, prefix)
    if found is None:
        return None
    line, exclude = found
    text = exclude.read_text() if exclude.exists() else ""
    if line not in text.splitlines():
        exclude.parent.mkdir(parents=True, exist_ok=True)
        with exclude.open("a", encoding="utf-8") as f:
            f.write(("\n" if text and not text.endswith("\n") else "") + line + "\n")
    return line
