"""Six deterministic linter classes, run over the in-memory shaped result (final full text + intent), no LLM call (fast, precise, injection-proof).

The six classes (validate-store §Validate): safety skills_guard / structure #416 / LED present /
content complete / global repo-agnostic / self-produced tag (only touch self-produced). Produces a
verdict {ok, findings:[(family, detail)]}; non-empty findings = reject. create is exempt from the
"self-produced" check (its tag is stamped after all six classes pass, by promoter).

When base_dir is given, the #416 "referenced .py syntax" check is added (a referenced, existing .py
must parse). target_is_agent_created is passed in by promoter after reading the sidecar; on create it
is None and exempt. When body=None (a delete's shaped result = removal, no body), the four
body-dependent classes (safety/structure/complete/global) are skipped, leaving only the LED +
self-produced checks.
"""
import ast
import re

from autoharness.lib import skills_guard

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
_PLACEHOLDER = re.compile(r"\b(TODO|FIXME|XXX)\b|<[A-Z][A-Z_]{2,}>")
_ABS_PATH = re.compile(r"(?:/home/|/Users/|/root/)[^\s`)\]]+|[A-Za-z]:\\[^\s`)\]]+")
_PY_REF = re.compile(r"[\w./-]+\.py")
_MODIFY = ("update", "patch", "delete")


def _frontmatter(body):
    m = _FRONTMATTER.match(body)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        s = line.strip()
        if not s or s.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm


def _structure(body, base_dir):
    findings = []
    fm = _frontmatter(body)
    if fm is None:
        findings.append(("structure", "missing/invalid frontmatter"))
        return findings
    if not fm.get("name"):
        findings.append(("structure", "missing name"))
    if not fm.get("description"):
        findings.append(("structure", "missing description"))
    if base_dir is not None:
        for ref in set(_PY_REF.findall(body)):
            f = base_dir / ref
            if f.is_file():
                try:
                    ast.parse(f.read_text())
                except SyntaxError as exc:
                    findings.append(("structure", f"referenced {ref} has syntax error: {exc}"))
    return findings


def structure(body):
    return _structure(body, None)


def validate(intent, body, *, target_is_agent_created=None, repo_name=None, base_dir=None):
    findings = []

    if body is not None:
        guard = skills_guard.scan(body)
        if guard:
            findings.append(("safety", guard))

        findings += _structure(body, base_dir)

        if _PLACEHOLDER.search(body):
            findings.append(("completeness", "contains TODO/placeholder"))

        if intent.get("level") == "global":
            markers = _ABS_PATH.findall(body)
            if repo_name and repo_name in body:
                markers.append(repo_name)
            if markers:
                findings.append(("global_repo_agnostic", markers))

    if not (intent.get("reason") or "").strip() or not (intent.get("evidence") or "").strip():
        findings.append(("led", "intent missing reason/evidence"))

    if intent.get("action") in _MODIFY and target_is_agent_created is not True:
        findings.append(("self_produced", "target live skill not created_by:agent"))

    return {"ok": not findings, "findings": findings}
