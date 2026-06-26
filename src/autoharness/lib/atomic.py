"""POSIX 原子写原语：temp 同目录 + fsync + os.replace —— live 永不半态。

validate-store 的"唯一落盘 = temp 同目录 + os.replace"就在此一处实现，skill_store / sidecar /
counters 全复用。写中途崩溃只会留同目录 .tmp 孤儿（由 skill_store 启动 sweep），目标文件
要么是旧内容、要么是新内容，绝无半写。
"""
import os
import tempfile
from pathlib import Path


def write_bytes(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def write_text(path, text):
    write_bytes(path, text.encode("utf-8"))
