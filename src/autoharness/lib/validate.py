"""确定性 linter 六类，跑在内存成型结果（最终全文 + intent）上、不调 LLM（快、精确、不可注入）。

六类（validate-store §Validate）：安全 skills_guard / 结构 #416 / LED 有 / 内容完整 /
global repo-agnostic / 自产标签（只动自产）。产 verdict {ok, findings:[(family, detail)]}；
findings 非空即 reject。create 豁免「自产」查（其打标在六类全 pass 之后，由 promoter 盖）。

base_dir 给定时附加 #416 的「引用 .py 语法」查（被引且存在的 .py 必须可解析）。
target_is_agent_created 由 promoter 读 sidecar 传入；create 时为 None、豁免。
body=None（delete 成型结果=移除、无正文）时跳过依赖 body 的四类（安全/结构/完整/global），
只留 LED + 自产两查。
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
