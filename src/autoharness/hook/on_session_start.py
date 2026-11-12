"""MNG lazy recompute: at SessionStart, compute over the accumulated ledger now → archive inactive symbols, running before this session's recall.

mng.md: a non-resident host has no background sweep, so eviction rides SessionStart — read the sidecar
(use/view counters + anchor) + the layer request counters (denominator) accumulated watermark, run the
lifecycle decision, and move the to-archive list out of the live tree one by one (archiving = moving the
directory out of recall, reversible). The decision reads only accumulated quantities (not what this
session happened to see) → any repo's SessionStart reaches the same conclusion. Once per session, no
throttling. Manages only self-produced symbols (native / user skills stay outside the pool, preserving
zero intrusion).

ponytail: GC of orphan session counts (residue from crashed sessions) needs a session-liveness signal to sweep safely (a naive sweep would wrongly delete a concurrent session's live count), so it is deferred until that signal exists — the clear_session primitive is ready (Phase 4), policy left open in cap.md/mng.md.
"""
import json
import logging
import os
import uuid
from pathlib import Path

from autoharness import config
from autoharness.hook import recovery
from autoharness.lib import counters, layer, lifecycle, sidecar, skill_store, validate

log = logging.getLogger(__name__)

# Claude Code already injects every available skill name and full description. SessionStart adds only
# autoharness ownership metadata the native list lacks: category and layer. Repeating descriptions
# wastes context and makes large hook output get persisted behind a short preview.
INDEX_HEADER = (
    "Autoharness-managed skills are already present with full descriptions in Claude Code's native "
    "skill list. You MUST consider loading a matching skill before proceeding. This compact map adds "
    "category and ownership layer only."
)


def _sanitize(text, limit):
    return " ".join(str(text).split())[:limit]  # line-based surface: newlines are forgery, collapse them


def _read_hint(roots, cwd):
    """A linked worktree's project layer is remapped to the main checkout (layer.default_root),
    which the host does not scan for skills — so from a worktree session those skills are listed
    here but the Skill tool cannot load them. Point the model at the files instead."""
    if not cwd:
        return None
    skills = layer.skills_dir(layer.PROJECT, roots.get(layer.PROJECT)).resolve()
    if Path(cwd).resolve().is_relative_to(skills.parent.parent):
        return None
    return (f"[project] skills live outside this checkout, so the Skill tool cannot load them: "
            f"Read {skills}/<name>/SKILL.md instead.")


def _compact_map(groups, hint=None):
    entries = [(category, line) for category in sorted(groups) for line in sorted(groups[category])]
    lines = [INDEX_HEADER]
    if hint:
        lines.extend(["", _sanitize(hint, 512)])
    lines.append("")
    included = 0
    current_category = None
    for category, entry in entries:
        addition = ([f"## {category}"] if category != current_category else []) + [entry]
        remaining = len(entries) - included - 1
        tail = (["", f"... {remaining} more managed skills; use the native list for the complete set."]
                if remaining else [])
        if len("\n".join(lines + addition + tail).encode("utf-8")) > config.SESSION_INDEX_MAX_BYTES:
            break
        lines.extend(addition)
        current_category = category
        included += 1
    omitted = len(entries) - included
    if omitted:
        lines.extend(["", f"... {omitted} more managed skills; use the native list for the complete set."])
    return "\n".join(lines)


def recall_index(roots, cwd=None):
    if config.INDEX_SUSPENDED:
        return None
    groups, has_project = {}, False
    for lyr in config.active_layers():
        root = roots.get(lyr)
        skills = layer.skills_dir(lyr, root)
        if not skills.exists():
            continue
        for path in skills.glob(f"*/{skill_store.SKILL_FILE}"):
            name = path.parent.name
            try:
                layer._check_name(name)
            except ValueError:
                continue  # handwritten skills are outside the managed pool
            try:
                managed = sidecar.is_agent_created(lyr, name, root)
            except (OSError, UnicodeError, ValueError, TypeError, AttributeError):
                log.warning("skipping skill with unreadable sidecar: %s", path.parent)
                continue
            if not managed:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                log.warning("skipping unreadable skill description: %s", path)
                continue
            fm = validate._frontmatter(text) or {}
            cat = _sanitize(fm.get("category") or "general", 64) or "general"
            groups.setdefault(cat, []).append(f"- {_sanitize(name, 64)} [{lyr}]")
            has_project = has_project or lyr == layer.PROJECT
    if not groups:
        return None  # empty library -> zero injection
    hint = _read_hint(roots, cwd) if has_project else None
    return _compact_map(groups, hint)


def last_run_summary(roots):
    """One-line anti-silence digest of the previous drain (validate-store §verdict visibility):
    read once, then consume — the account file under runs/ keeps the durable record."""
    p = layer.state_dir(layer.PROJECT, roots.get(layer.PROJECT)) / "last_run.json"
    if not p.exists():
        return None
    # Each claimant owns a distinct destination: another drain may publish a new
    # last_run.json before this consumer has finished reading its claimed record.
    consumed = p.with_name(f"{p.name}.{uuid.uuid4().hex}.consuming")
    try:
        p.rename(consumed)
    except OSError:
        return None
    try:
        last = json.loads(consumed.read_text(encoding="utf-8"))
        if not isinstance(last, dict):
            return None
    except (ValueError, OSError):
        return None
    finally:
        try:
            consumed.unlink()
        except OSError:
            pass
    # name the run so the numbers stay traceable when a Stop drained a dead sibling's queue
    line = (f"autoharness last run ({last.get('run_id', 'unknown')}): landed {last.get('landed', 0)}, "
            f"rejected {last.get('rejected', 0)}")
    families = last.get("families")
    if isinstance(families, list) and families and all(isinstance(f, str) for f in families):
        line += f" ({', '.join(families)})"
    if last.get("absorbed"):
        line += f"; merged {last['absorbed']} into umbrellas"
    if last.get("uncategorized"):
        line += f"; {last['uncategorized']} landed with no category (grouped under general)"
    return line


def _members(lyr, root):
    skills = layer.skills_dir(lyr, root)
    if not skills.exists():
        return []
    members = []
    for path in skills.glob(f"*/{skill_store.SKILL_FILE}"):
        name = path.parent.name
        try:
            layer._check_name(name)
        except ValueError:
            continue
        if not sidecar.is_agent_created(lyr, name, root):
            continue
        s = sidecar.read(lyr, name, root)
        members.append({"name": name, "use": s.get("use", 0), "view": s.get("view", 0),
                        "anchor": s.get("anchor", 0)})
    return members


def on_session_start(event=None, *, roots=None):
    if os.environ.get(config.CHILD_SESSION_ENV):
        # a reflector/curator child: it must not consume the user's last-run line, run the archive pass
        # beside the parent, or get a second index on top of its bundle
        return {"archived": {}, "context": None, "reason": "recursion_guard"}
    roots = roots or {}
    recovery.recover(roots=roots)
    archived = {}
    for lyr in config.active_layers():
        root = roots.get(lyr)
        names = lifecycle.evaluate(
            _members(lyr, root), counters.request_count(lyr, root),
            maturity=config.MATURITY_THRESHOLD[lyr], capacity=config.CAPACITY[lyr],
            review_suspended=config.GRADUATION_REVIEW_SUSPENDED,
        )
        for name in names:
            skill_store.archive(lyr, name, root)
        archived[lyr] = names
    parts = [last_run_summary(roots), recall_index(roots, (event or {}).get("cwd"))]  # index built after archiving
    context = "\n\n".join(p for p in parts if p) or None
    return {"archived": archived, "context": context}
