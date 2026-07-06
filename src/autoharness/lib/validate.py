"""Six deterministic linter classes, run over the in-memory shaped result (final full text + intent), no LLM call (fast, precise, injection-proof).

The six classes (validate-store §Validate): safety skills_guard / structure #416 / LED present /
content complete / global repo-agnostic / self-produced tag (only touch self-produced). Produces a
verdict {ok, findings:[(family, detail)]}; non-empty findings = reject. create is exempt from the
"self-produced" check (its tag is stamped after all six classes pass, by promoter).

When base_dir is given, the #416 "referenced .py syntax" check is added (a referenced, existing .py
must parse), plus the subfile-reference check: a whitelisted-dir path mentioned in the body must be
carried in the intent's `files` or already live under base_dir. target_is_agent_created is passed in
by promoter after reading the sidecar; on create it is None and exempt. When body=None (delete /
remove_file shape to no body change), the four body-dependent classes (safety/structure/complete/
global) are skipped, leaving the LED + self-produced checks — remove_file adds its path gate
(check_remove_path: subfile whitelist + evidence-slice deny).

folder-skill `files` (relative path → content) gets its own `files` family (check_files: shape, path
gate via layer.check_subfile, count/size caps) + the pointer rule (every carried subfile must be
referenced in the body) + per-subfile safety and global scans — otherwise subfiles would be a trivial
bypass of both gates. Promoter-materialized `references/evidence-*` slices are off-limits to intents
in both directions: carrying one in `files` and removing one via remove_file are rejected.
"""
import ast
import re

from autoharness import config
from autoharness.lib import layer, skills_guard

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
_PLACEHOLDER = re.compile(r"\b(TODO|FIXME|XXX):|<[A-Z][A-Z_]{2,}>")
_ABS_PATH = re.compile(r"(?:/home/|/Users/|/root/)[^\s`)\]]+|[A-Za-z]:\\[^\s`)\]]+")
_PY_REF = re.compile(r"[\w./-]+\.py")
_SUBFILE_REF = re.compile(r"\b(?:{})/[A-Za-z0-9._/-]+".format("|".join(layer.SUBFILE_DIRS)))
_MODIFY = ("update", "patch", "remove_file", "delete")


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


def _evidence_slice_denied(rel):
    if rel.startswith(layer.EVIDENCE_PREFIX):
        return [("files", f"{rel}: promoter-materialized evidence slices are off-limits to intents")]
    return []


def check_remove_path(rel):
    try:
        layer.check_subfile(rel)
    except ValueError as exc:
        return [("files", str(exc))]
    return _evidence_slice_denied(rel)


def check_files(files):
    if files is None:
        return []
    if not isinstance(files, dict):
        return [("files", "files must be a map of relative path -> content")]
    findings = []
    if len(files) > config.STAGE_MAX_FILES:
        findings.append(("files", f"more than {config.STAGE_MAX_FILES} subfiles"))
    total = 0
    for rel, content in files.items():
        try:
            layer.check_subfile(rel)
        except ValueError as exc:
            findings.append(("files", str(exc)))
            continue
        if not isinstance(content, str):
            findings.append(("files", f"{rel}: content must be a string"))
            continue
        findings += _evidence_slice_denied(rel)
        size = len(content.encode("utf-8"))
        total += size
        if size > config.STAGE_MAX_FILE_BYTES:
            findings.append(("files", f"{rel} exceeds {config.STAGE_MAX_FILE_BYTES} bytes"))
    if total > config.STAGE_MAX_FILES_TOTAL_BYTES:
        findings.append(("files", f"subfiles exceed {config.STAGE_MAX_FILES_TOTAL_BYTES} bytes total"))
    return findings


def _structure(body, base_dir, files=None):
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
        for ref in set(_SUBFILE_REF.findall(body)):
            if ref not in (files or {}) and not (base_dir / ref).is_file():
                findings.append(("structure", f"referenced {ref} neither carried in intent nor live"))
    for rel in files or {}:
        if isinstance(rel, str) and rel not in body:
            findings.append(("structure", f"carried subfile {rel} not referenced in SKILL.md body"))
    return findings


def structure(body, files=None):
    return _structure(body, None, files)


def validate(intent, body, *, target_is_agent_created=None, repo_name=None, base_dir=None):
    findings = []
    files = intent.get("files")

    if body is not None:
        guard = skills_guard.scan(body)
        if guard:
            findings.append(("safety", guard))

        findings += _structure(body, base_dir, files)
        findings += check_files(files)

        if _PLACEHOLDER.search(body):
            findings.append(("completeness", "contains TODO/placeholder"))

        contents = [v for v in (files or {}).values() if isinstance(v, str)]
        for content in contents:
            guard = skills_guard.scan(content)
            if guard:
                findings.append(("safety", guard))

        if intent.get("level") == "global":
            markers = _ABS_PATH.findall(body)
            for content in contents:
                markers += _ABS_PATH.findall(content)
            if repo_name and (repo_name in body or any(repo_name in c for c in contents)):
                markers.append(repo_name)
            if markers:
                findings.append(("global_repo_agnostic", markers))

    if intent.get("action") == "remove_file":
        findings += check_remove_path(intent.get("path"))

    if not (intent.get("reason") or "").strip() or not (intent.get("evidence") or "").strip():
        findings.append(("led", "intent missing reason/evidence"))

    if intent.get("action") in _MODIFY and target_is_agent_created is not True:
        findings.append(("self_produced", "target live skill not created_by:agent"))

    return {"ok": not findings, "findings": findings}
