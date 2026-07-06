"""REF launch vehicle: deterministically assemble the reflector input → detached spawn a child session → connect to promoter.drain.

architecture line 29 / [reflector-subagent] / [cap]: at trigger time CAP gives "redacted episode window +
trigger cadence"; this step assembles the three pieces (window + the existing skill description index
(compare-first dedupe source, skips archived) + the single-source format_spec) and feeds them via
stdin to the cross-process reflector — nothing is persisted; the bundle lives only in the pipe. spawn sets CHILD_SESSION_ENV (recursion guard) +
injects run_id/root via env (stage_skill uses these to append back to the queue), then drains the intent
queue to disk after the child session ends. Authoring and landing are fully split across processes from
here: the reflector only appends intents, the promoter exclusively validates and lands.

ponytail: run() is the body of the "detached background job" (synchronous spawn→wait→drain); the "do not block the host Stop" detach is started in the background at the hook top level by the Phase 7 dispatch calling run(). spawn_fn is injectable (system tests use a fake reflector script in place of the real claude). Precise handling of the transcript upper-bound race (cap.md open) is still tolerated at v0.
"""
import os
import subprocess
import sys
from pathlib import Path

from autoharness import config
from autoharness.hook import capture, promoter
from autoharness.lib import counters, layer, skill_store, validate


def description_index(roots=None):
    roots = roots or {}
    lines = []
    for lyr in layer.LAYERS:
        skills = layer.skills_dir(lyr, roots.get(lyr))
        if not skills.exists():
            continue
        for path in sorted(skills.glob(f"*/{skill_store.SKILL_FILE}")):
            fm = validate._frontmatter(path.read_text()) or {}
            name = fm.get("name") or path.parent.name
            desc = fm.get("description") or "(no description)"
            lines.append(f"- {name} [{lyr}]: {desc}")
    return "\n".join(lines) if lines else "(no live skills yet)"


def build_bundle(window, index, spec):
    return (
        "# Episode window (redacted)\n\n" + window
        + "\n\n# Existing skills (compare-first: dedupe / patch / where)\n\n" + index
        + "\n\n# Authoring + format spec (write to satisfy this)\n\n" + spec + "\n"
    )


def build_command(*, agent, claude_bin):
    # Reflection is an unattended background job — nobody is there to approve tool calls, so skip the
    # permission prompt. The security boundary is held by the agent's tools allowlist
    # (Read/Grep/Glob/stage_skill) + the top-level PreToolUse write backstop, not by the prompt.
    # (live e2e: a reflector's real stage_skill call gets blocked by the permission gate and can only
    # "narrate"; only with this flag does it land.)
    return [claude_bin, "-p", "--agent", agent, "--dangerously-skip-permissions"]


def child_env(run_id, root, *, base_env=None):
    env = dict(os.environ if base_env is None else base_env)
    env[config.CHILD_SESSION_ENV] = "1"
    env[config.RUN_ID_ENV] = run_id
    env[config.PROJECT_ROOT_ENV] = str(root)
    return env


def _detached_spawn(argv, env, bundle):
    subprocess.run(argv, input=bundle, text=True, env=env, capture_output=True, check=False)


def run(window_text, run_id, *, roots, repo_name=None, agent=None, claude_bin=None,
        spec_path=None, spawn_fn=None):
    roots = roots or {}
    proot = roots.get(layer.PROJECT)
    spec = (spec_path or config.FORMAT_SPEC).read_text()
    bundle = build_bundle(window_text, description_index(roots), spec)

    argv = build_command(agent=agent or config.REFLECTOR_AGENT,
                         claude_bin=claude_bin or config.CLAUDE_BIN)
    env = child_env(run_id, proot)
    (spawn_fn or _detached_spawn)(argv, env, bundle)

    return promoter.drain(run_id, roots=roots, repo_name=repo_name)


def main(argv=None):
    transcript_path, session_id, run_id, proot, groot = argv if argv is not None else sys.argv[1:]
    roots = {layer.PROJECT: Path(proot), layer.GLOBAL: Path(groot)}
    offset = counters.session_offset(session_id, roots[layer.PROJECT])
    window_text, new_offset = capture.window(transcript_path, offset)
    result = run(window_text, run_id, roots=roots)
    counters.write_session_offset(session_id, new_offset, roots[layer.PROJECT])
    return result


if __name__ == "__main__":
    main()
