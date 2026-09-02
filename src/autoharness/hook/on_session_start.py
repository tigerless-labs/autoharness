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
DEMOTION_NOTE = (
    "(Categories marked [names only] are outside this session's budget, so their descriptions are "
    "omitted — the skills still load normally by name.)"
)


def _sanitize(text, limit):
    return " ".join(str(text).split())[:limit]  # line-based surface: newlines are forgery, collapse them


def _demoted(groups, budget):
    """Which categories collapse to a names-only line so the index fits its budget.

    Ranked by use per entry — what a category earns for the lines it costs — ascending, so the
    coldest give up their descriptions first. Demotion is the only lever: an entry is never dropped
    (mng.md), so the floor is one line per category and a budget below that simply demotes all.
    """
    cost = sum(1 + len(v) for v in groups.values())
    if not budget or cost <= budget:
        return frozenset()
    ranked = sorted(groups, key=lambda c: (sum(u for _, u in groups[c]) / len(groups[c]), c))
    demoted = set()
    for cat in ranked:
        if cost <= budget:
            break
        demoted.add(cat)
        cost -= len(groups[cat])  # the header line stays, its entries fold into it
    return frozenset(demoted)


def recall_index(roots):
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
            desc = _sanitize(fm.get("description") or "(no description)", config.INDEX_DESC_MAX_CHARS)
            cat = _sanitize(fm.get("category") or "general", 64) or "general"
            entry = f"- {_sanitize(name, 64)} [{lyr}]: {desc}"
            groups.setdefault(cat, []).append((entry, sidecar.read(lyr, name, root).get("use", 0)))
    if not groups:
        return None  # empty library -> zero injection
    demoted = _demoted(groups, config.INDEX_MAX_LINES)
    lines = [INDEX_HEADER, ""]
    if demoted:
        lines += [DEMOTION_NOTE, ""]
    for cat in sorted(groups):
        entries = sorted(e for e, _ in groups[cat])
        if cat in demoted:
            names = ", ".join(e.split(" [", 1)[0][2:] for e in entries)
            lines.append(f"## {cat} [names only]: {names}")
            continue
        lines.append(f"## {cat}")
        lines.extend(entries)
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
