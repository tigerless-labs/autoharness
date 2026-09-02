import re
import sys
from pathlib import Path

_MD_LINK = re.compile(r"\]\(\s*([^)\s]+?\.md)(?:#[^)]*)?\s*\)")
_EXTERNAL = re.compile(r"^[a-z][a-z0-9+.-]*://")


def local_md_targets(text):
    for raw in _MD_LINK.findall(text):
        if not _EXTERNAL.match(raw):
            yield raw


def scan(docs_root):
    docs_root = Path(docs_root)
    dangling = []
    for md in sorted(docs_root.rglob("*.md")):
        if ".archive" in md.parts:
            continue  # retired docs keep their own internal links; they are a snapshot, not live prose
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for target in local_md_targets(line):
                if not (md.parent / target).resolve().exists():
                    dangling.append((md, lineno, target))
    return dangling


def selftest():
    import tempfile

    assert list(local_md_targets("see [x](a/b.md) and [ext](https://h.md)")) == ["a/b.md"]
    assert list(local_md_targets("anchor [y](../c/d.md#sec) ok")) == ["../c/d.md"]
    assert list(local_md_targets("plain `path.md` backtick, [[wiki]] prose")) == []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".archive").mkdir()
        (root / ".archive" / "old.md").write_text("[gone](nowhere.md)")
        (root / "live.md").write_text("[gone](nowhere.md)")
        assert [d[0].name for d in scan(root)] == ["live.md"]
    print("selftest: ok")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    root = Path(argv[1]) if len(argv) > 1 else Path("docs")
    dangling = scan(root)
    if dangling:
        for md, lineno, target in dangling:
            print(f"DANGLING {md}:{lineno} -> {target}")
        print(f"\n{len(dangling)} dangling link(s)")
        return 1
    print(f"ok: no dangling links under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
