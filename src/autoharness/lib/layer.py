"""Resolves a layer name into its on-disk location — the one place where a layer surfaces as a path.

The rest of the code is layer-agnostic and passes layer in as an argument. Unknown layers / unsafe
symbol names are always rejected (fail-safe, deny-by-default), because this is the chokepoint that
builds filesystem paths: privilege escalation / path traversal must be stopped here.

The project layer's identity is the session cwd — except inside a linked git worktree, where it is
remapped to the main worktree root, so counters / intents / skills from all worktrees of one repo
land in one place and survive worktree removal. Only the linked-worktree case is remapped (git-dir
differs from git-common-dir): plain repos, repo subdirectories, and non-git directories keep cwd
verbatim, so a nested project can never be attributed to an enclosing repo. Any git failure falls
back to cwd (fail-safe).
"""
import re
import subprocess
from functools import cache
from pathlib import Path

GLOBAL = "global"
PROJECT = "project"
LAYERS = (GLOBAL, PROJECT)

_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _check_layer(layer):
    if layer not in LAYERS:
        raise ValueError(f"unknown layer: {layer!r} (expected one of {LAYERS})")


# a name becomes a directory or file, and atomic writes add `.<8 chars>.tmp` to it: stay well inside
# NAME_MAX (255 bytes), and away from what Windows refuses (reserved device names, a trailing dot)
MAX_NAME_LEN = 100
_WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}


def _check_name(name):
    if not isinstance(name, str) or ".." in name or not _SAFE_NAME.match(name):
        raise ValueError(f"unsafe symbol name: {name!r}")


def check_new_name(name):
    """A name autoharness is about to create: safe, and usable on every filesystem. Existing names
    (a user's `con` skill, a long legacy one) are only held to _check_name, so reading never breaks."""
    _check_name(name)
    if len(name) > MAX_NAME_LEN or name.endswith(".") or name.split(".")[0].lower() in _WINDOWS_RESERVED:
        raise ValueError(f"unusable new name: {name!r} (over {MAX_NAME_LEN} chars, a trailing dot, or "
                         "reserved on Windows)")


def _main_worktree_root(cwd):
    return _main_worktree_root_resolved(str(Path(cwd).resolve()))


@cache
def _main_worktree_root_resolved(cwd):
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--git-dir", "--git-common-dir"],
            cwd=cwd, capture_output=True, text=True, timeout=5,
        )
        lines = proc.stdout.splitlines()
        if proc.returncode != 0 or len(lines) < 2:
            return Path(cwd)
        git_dir, common_dir = ((Path(cwd) / line).resolve() for line in lines[:2])
        if git_dir != common_dir:
            return common_dir.parent
    except (OSError, subprocess.SubprocessError):
        pass
    return Path(cwd)


def default_root(layer):
    _check_layer(layer)
    if layer == GLOBAL:
        return Path.home() / ".claude"
    return _main_worktree_root(str(Path.cwd())) / ".claude"


def _root(layer, root):
    _check_layer(layer)
    return Path(root) if root is not None else default_root(layer)


def skills_dir(layer, root=None):
    return _root(layer, root) / "skills"


def archive_dir(layer, root=None):
    return skills_dir(layer, root) / ".archive"


def state_dir(layer, root=None):
    return _root(layer, root) / "autoharness"


def symbol_dir(layer, name, root=None):
    _check_name(name)
    return skills_dir(layer, root) / name


SUBFILE_DIRS = ("scripts", "templates", "assets", "references")
EVIDENCE_PREFIX = "references/evidence-"


def check_subfile(rel, *, new=False):
    if not isinstance(rel, str) or not rel or ".." in rel or "\\" in rel:
        raise ValueError(f"unsafe subfile path: {rel!r}")
    segments = rel.split("/")
    if len(segments) < 2 or segments[0] not in SUBFILE_DIRS:
        raise ValueError(f"subfile path must sit under one of {SUBFILE_DIRS}: {rel!r}")
    for segment in segments:
        (check_new_name if new else _check_name)(segment)


def subfile_path(layer, name, rel, root=None):
    check_subfile(rel)
    return symbol_dir(layer, name, root) / rel
