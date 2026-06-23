import sys
from pathlib import Path

CONTRACT = {
    "direction": {"required": ["id", "type"]},
    "idea": {"required": ["id", "type", "status"], "enums": {"status": ["候选", "采纳", "存疑"]}},
    "design": {"required": ["id", "type"]},
    "decision": {"required": ["id", "type", "status", "affects"], "enums": {"status": ["open", "resolved"]}},
    "adr": {"required": ["id", "type", "status"], "enums": {"status": ["proposed", "accepted", "superseded"]}},
}


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" in line and not line.startswith((" ", "\t")):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return None


def validate(fields):
    errors = []
    kind = fields.get("type")
    if kind not in CONTRACT:
        return [f"unknown or missing type: {kind!r}"]
    spec = CONTRACT[kind]
    for field in spec["required"]:
        if not fields.get(field):
            errors.append(f"missing required field: {field}")
    for field, allowed in spec.get("enums", {}).items():
        value = fields.get(field)
        if value and value not in allowed:
            errors.append(f"{field}={value!r} not in {allowed}")
    return errors


def scan(root):
    problems = []
    for md in sorted(Path(root).rglob("*.md")):
        if md.name == "index.md":
            continue
        fields = frontmatter(md.read_text(encoding="utf-8"))
        if fields is None:
            continue
        for err in validate(fields):
            problems.append((md, err))
    return problems


def selftest():
    good = {"id": "D-1", "type": "decision", "status": "open", "affects": "[OPT]"}
    assert validate(good) == [], "valid decision must pass"
    assert validate({"type": "idea", "status": "采纳"}), "missing id must fail"
    assert validate({"id": "i", "type": "idea", "status": "x"}), "bad enum must fail"
    assert validate({"id": "z", "type": "bogus"}), "unknown type must fail"
    assert frontmatter("no frontmatter here") is None
    assert frontmatter("---\ntype: idea\nid: a\nstatus: 采纳\n---\nbody")["type"] == "idea"
    print("selftest: ok")


def main(argv):
    if "--selftest" in argv:
        selftest()
        return 0
    root = Path(argv[1]) if len(argv) > 1 else Path("docs/research-loom")
    problems = scan(root)
    if problems:
        for md, err in problems:
            print(f"INVALID {md}: {err}")
        print(f"\n{len(problems)} frontmatter problem(s)")
        return 1
    print(f"ok: frontmatter valid under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
