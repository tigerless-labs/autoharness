"""REF 启动载体：确定性拼装 reflector 输入 → detached spawn 子会话 → 接 promoter.drain。

architecture line 29 / [reflector-subagent] / [cap]：CAP 触发那刻给「脱敏 episode 窗 + 触发节奏」，
本步拼三件套（窗 + 现有 skill 描述索引(compare-first 去重源，跳归档) + 单一来源 format_spec）
落盘 + 经 stdin 喂跨进程 reflector，spawn 用 CHILD_SESSION_ENV 置位（递归 guard）+ run_id/root
经环境注入（stage_skill 据此 append 回队列），等子会话结束后 drain intent 队列落盘。author 与
land 自此彻底分进程：reflector 只 append intent、promoter 独占校验·落盘。

ponytail: run() 是「detached 后台作业」的作业体（同步 spawn→wait→drain）；「不堵宿主 Stop」的
detach 由 Phase 7 dispatch 在 hook 顶层后台启 run()。spawn_fn 可注入（system 测用 fake reflector
脚本替真 claude）。transcript 上界 race 精确化（cap.md 待解）仍 v0 容忍。
"""
import os
import subprocess
import sys
from pathlib import Path

from autoharness import config
from autoharness.hook import capture, promoter
from autoharness.lib import atomic, layer, skill_store, validate


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
    return [claude_bin, "-p", "--agent", agent]


def child_env(run_id, root, *, base_env=None):
    env = dict(os.environ if base_env is None else base_env)
    env[config.CHILD_SESSION_ENV] = "1"
    env[config.RUN_ID_ENV] = run_id
    env[config.PROJECT_ROOT_ENV] = str(root)
    return env


def _detached_spawn(argv, env, bundle):
    subprocess.run(argv, input=bundle, text=True, env=env, capture_output=True, check=False)


def run(window_text, run_id, *, roots, repo_name=None, agent=None, claude_bin=None,
        spec_path=None, anchor=0, spawn_fn=None):
    roots = roots or {}
    proot = roots.get(layer.PROJECT)
    spec = (spec_path or config.FORMAT_SPEC).read_text()
    bundle = build_bundle(window_text, description_index(roots), spec)
    atomic.write_text(layer.state_dir(layer.PROJECT, proot) / "handoff" / f"{run_id}.md", bundle)

    argv = build_command(agent=agent or config.REFLECTOR_AGENT,
                         claude_bin=claude_bin or config.CLAUDE_BIN)
    env = child_env(run_id, proot)
    (spawn_fn or _detached_spawn)(argv, env, bundle)

    return promoter.drain(run_id, roots=roots, repo_name=repo_name, anchor=anchor)


def main(argv=None):
    transcript_path, n, run_id, proot, groot = argv if argv is not None else sys.argv[1:]
    roots = {layer.PROJECT: Path(proot), layer.GLOBAL: Path(groot)}
    run(capture.window(transcript_path, int(n)), run_id, roots=roots)


if __name__ == "__main__":
    main()
