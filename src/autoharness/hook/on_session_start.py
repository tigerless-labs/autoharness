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

from autoharness import config
from autoharness.lib import counters, layer, lifecycle, sidecar, skill_store, validate

# Recall self-injection (mng.md §召回面自持): the host's native description recall stays untouched;
# this compact index of self-produced skills rides SessionStart additionalContext so "whether the
# library is offered" is our own config, not host behavior. Grouped by frontmatter category
# (open set, absent -> general), alphabetical within a group, layer-tagged per line.
INDEX_HEADER = (
    "Self-accumulated skills (autoharness-managed). When the task at hand matches a "
    "description below, you MUST consider loading that skill before proceeding."
)


def _sanitize(text, limit):
    return " ".join(str(text).split())[:limit]  # line-based surface: newlines are forgery, collapse them


def _fit(text, limit):
    """Truncate with an ellipsis so a cut line reads as cut (hermes' index does the same).

    New descriptions are held inside the budget by the promoter, so this only fires on skills that
    predate the gate — and there it matters that the reader can tell the line was severed rather
    than take a fragment for the whole trigger."""
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[:limit - 3] + "..."


def recall_index(roots):
    if config.INDEX_SUSPENDED:
        return None
    groups = {}
    for lyr in layer.LAYERS:
        root = roots.get(lyr)
        skills = layer.skills_dir(lyr, root)
        if not skills.exists():
            continue
        for path in skills.glob(f"*/{skill_store.SKILL_FILE}"):
            name = path.parent.name
            if not sidecar.is_agent_created(lyr, name, root):
                continue
            fm = validate._frontmatter(path.read_text()) or {}
            desc = _fit(fm.get("description") or "(no description)", config.INDEX_DESC_MAX_CHARS)
            cat = _sanitize(fm.get("category") or "general", 64) or "general"
            groups.setdefault(cat, []).append(f"- {_sanitize(name, 64)} [{lyr}]: {desc}")
    if not groups:
        return None  # empty library -> zero injection
    lines = [INDEX_HEADER, ""]
    for cat in sorted(groups):
        lines.append(f"## {cat}")
        lines.extend(sorted(groups[cat]))
    return "\n".join(lines)


def last_run_summary(roots):
    """One-line anti-silence digest of the previous drain (validate-store §verdict visibility):
    read once, then consume — the account file under runs/ keeps the durable record."""
    p = layer.state_dir(layer.PROJECT, roots.get(layer.PROJECT)) / "last_run.json"
    if not p.exists():
        return None
    try:
        last = json.loads(p.read_text())
    except (ValueError, OSError):
        return None
    finally:
        try:
            p.unlink()
        except OSError:
            pass
    line = (f"autoharness last run: landed {last.get('landed', 0)}, "
            f"rejected {last.get('rejected', 0)}")
    if last.get("families"):
        line += f" ({', '.join(last['families'])})"
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
        if not sidecar.is_agent_created(lyr, name, root):
            continue
        s = sidecar.read(lyr, name, root)
        members.append({"name": name, "use": s.get("use", 0), "view": s.get("view", 0),
                        "anchor": s.get("anchor", 0)})
    return members


def on_session_start(event=None, *, roots=None):
    roots = roots or {}
    archived = {}
    for lyr in layer.LAYERS:
        root = roots.get(lyr)
        names = lifecycle.evaluate(
            _members(lyr, root), counters.request_count(lyr, root),
            maturity=config.MATURITY_THRESHOLD[lyr], capacity=config.CAPACITY[lyr],
            review_suspended=config.GRADUATION_REVIEW_SUSPENDED,
        )
        for name in names:
            skill_store.archive(lyr, name, root)
        archived[lyr] = names
    parts = [last_run_summary(roots), recall_index(roots)]  # index built after archiving
    context = "\n\n".join(p for p in parts if p) or None
    return {"archived": archived, "context": context}
