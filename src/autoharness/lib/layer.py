"""把 layer 名解析成落盘位 —— 层在代码里唯一显形为路径的地方。

其余代码层无关、把 layer 当入参传进来。未知层 / 不安全符号名一律拒（fail-safe，
deny-by-default），因为这是构造文件系统路径的咽喉，越权 / 路径穿越必须挡在此。
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
