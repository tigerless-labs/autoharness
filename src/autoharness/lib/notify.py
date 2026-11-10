"""Run-account notification: tell the operator the moment a run lands or rejects, not next session.

The SessionStart summary line is the only other surface, and it arrives one session late with counts
but no names. This pushes the same run account out once a drain has finished — opt-in, off by default:

- AUTOHARNESS_NOTIFY=desktop → a native notification (osascript on macOS, notify-send on Linux when
  present; anything else is a silent no-op).
- AUTOHARNESS_NOTIFY_CMD="<argv>" → run that command with the run record JSON on stdin and the
  one-line summary in AUTOHARNESS_NOTIFY_SUMMARY — the hook for Slack/webhooks/anything else.

Fail-open by construction: drain calls this only after the account is written and the queue cleared,
and send() swallows everything, so a missing binary, a non-zero exit or a hung command (bounded by
NOTIFY_TIMEOUT_S per channel) can delay a drain but never fail or replay one. Nothing goes through a
shell: skill names come from model-proposed intents (a rejected one can carry any string), so they
travel as argv / stdin data only, after the same redaction every other egress gets. The command runs
with the recursion guard set, so a notifier that itself launches `claude` is not captured or reflected.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

from autoharness import config
from autoharness.lib import redact

_TITLE = "autoharness"
_MAX_NAME = 64
_MAX_LISTED = 5  # names per summary bucket before "+N more": a notification body, not a report


def _clean(name):
    # redact before truncating: a cut can split a secret so its rule no longer matches
    s = redact.redact("".join(ch for ch in str(name or "?") if ch.isprintable()))
    return s[:_MAX_NAME] or "?"


def _listing(items):
    shown = ", ".join(items[:_MAX_LISTED])
    return shown + (f" +{len(items) - _MAX_LISTED} more" if len(items) > _MAX_LISTED else "")


def summary(rows):
    """One line naming what the run did: 'create foo, patch bar · rejected: baz'."""
    landed = [f"{r.get('action')} {_clean(r.get('name'))}" for r in rows if r.get("ok")]
    rejected = [_clean(r.get("name")) for r in rows if not r.get("ok")]
    parts = []
    if landed:
        parts.append(_listing(landed))
    if rejected:
        parts.append("rejected: " + _listing(rejected))
    return " · ".join(parts)


def _run(argv, *, stdin=None, env=None):
    subprocess.run(argv, input=stdin, stdin=None if stdin is not None else subprocess.DEVNULL,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", env=env,
                   timeout=config.NOTIFY_TIMEOUT_S, check=False)


def _desktop(line):
    if sys.platform == "darwin":
        # argv, not an interpolated -e string: the message is data AppleScript never parses
        _run(["osascript", "-e", "on run argv", "-e",
              "display notification (item 1 of argv) with title (item 2 of argv)", "-e", "end run",
              line, _TITLE])
    elif shutil.which("notify-send"):
        _run(["notify-send", _TITLE, line])


def _command(cmd, record, line):
    # POSIX shlex rules eat the backslashes of a Windows path; there the string goes to
    # CreateProcess as-is (still no shell) and the target parses it by the native rules.
    argv = cmd.strip() if os.name == "nt" else shlex.split(cmd)
    if not argv:
        return
    rows = [{**r, "name": _clean(r.get("name"))} for r in record.get("verdicts") or []]
    env = {**os.environ, "AUTOHARNESS_NOTIFY_SUMMARY": line, config.CHILD_SESSION_ENV: "1"}
    _run(argv, stdin=json.dumps({**record, "verdicts": rows}, ensure_ascii=False), env=env)


def send(record):
    """Push one run record ({"run_id", "verdicts"}) to whichever channels are enabled. Never raises."""
    mode, cmd = config.NOTIFY, config.NOTIFY_CMD
    if mode != "desktop" and not cmd:
        return
    try:
        line = summary(record.get("verdicts") or [])
    except Exception:
        return
    if not line:
        return
    for enabled, channel in ((mode == "desktop", lambda: _desktop(line)),
                             (bool(cmd), lambda: _command(cmd, record, line))):
        if not enabled:
            continue
        try:
            channel()
        except Exception:
            pass  # a notifier is a courtesy; the account is already durable and the queue cleared
