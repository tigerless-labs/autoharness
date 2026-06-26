"""skill CRUD：原子写 SKILL.md + 两层 find（同名跨两层报错消歧）+ 应用 delta + 归档 + 孤儿 .tmp sweep。

落盘只此一处用 atomic（temp 同目录 + os.replace），live 永不半态。find 扩 Hermes `_find_skill`
到 global+project 两层并集；同名跨两层 → 报错（promoter 解析 update/delete 层时据此消歧）。
apply_delta 要求 old_string 唯一命中（不存在 / 多处歧义都拒），确定性重建。archive 原子移 symbol_dir
进 `.archive`（保 LED/sidecar），delete 落地与 MNG（Phase 6）淘汰共用此一份。
"""
import os
import shutil

from autoharness.lib import atomic, layer

SKILL_FILE = "SKILL.md"


def skill_path(lyr, name, root=None):
    return layer.symbol_dir(lyr, name, root) / SKILL_FILE


def write_body(lyr, name, body, root=None):
    atomic.write_text(skill_path(lyr, name, root), body)


def read_body(lyr, name, root=None):
    p = skill_path(lyr, name, root)
    return p.read_text() if p.exists() else None


def exists(lyr, name, root=None):
    return skill_path(lyr, name, root).exists()


def find(name, roots=None):
    roots = roots or {}
    hits = [lyr for lyr in layer.LAYERS if exists(lyr, name, roots.get(lyr))]
    if len(hits) > 1:
        raise ValueError(f"ambiguous skill {name!r} present in layers {hits}")
    return hits[0] if hits else None


def apply_delta(body, old_string, new_string):
    count = body.count(old_string)
    if count == 0:
        raise ValueError("delta old_string not found in live body")
    if count > 1:
        raise ValueError("delta old_string is ambiguous (multiple matches)")
    return body.replace(old_string, new_string, 1)


def remove(lyr, name, root=None):
    sdir = layer.symbol_dir(lyr, name, root)
    if sdir.exists():
        shutil.rmtree(sdir)


def archive(lyr, name, root=None):
    sdir = layer.symbol_dir(lyr, name, root)
    if not sdir.exists():
        return None
    dest = layer.archive_dir(lyr, root) / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        shutil.rmtree(dest)
    os.replace(sdir, dest)
    return dest


def sweep_orphans(lyr, root=None):
    skills = layer.skills_dir(lyr, root)
    if not skills.exists():
        return []
    removed = []
    for tmp in skills.rglob("*.tmp"):
        tmp.unlink()
        removed.append(tmp)
    return removed
