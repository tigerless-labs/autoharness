"""Resolves a layer name into its on-disk location — the one place where a layer surfaces as a path.

The rest of the code is layer-agnostic and passes layer in as an argument. Unknown layers / unsafe
symbol names are always rejected (fail-safe, deny-by-default), because this is the chokepoint that
builds filesystem paths: privilege escalation / path traversal must be stopped here.
"""
import re
from pathlib import Path

GLOBAL = "global"
PROJECT = "project"
LAYERS = (GLOBAL, PROJECT)

_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def _check_layer(layer):
    if layer not in LAYERS:
        raise ValueError(f"unknown layer: {layer!r} (expected one of {LAYERS})")


def _check_name(name):
    if not isinstance(name, str) or ".." in name or not _SAFE_NAME.match(name):
        raise ValueError(f"unsafe symbol name: {name!r}")


def default_root(layer):
    _check_layer(layer)
    return Path.home() / ".claude" if layer == GLOBAL else Path.cwd() / ".claude"


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
