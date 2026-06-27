"""Full skill-lifecycle sandbox: birth → use → compete → archive → restore, driven through
the real dispatch + spawn + promoter + lifecycle. Only the reflector model is a canned stub
(fake_spawn stages one intent); everything else is the production path on an isolated tmp dir.

This is the deterministic counterpart to the live host runbook (experiments/E7_plugin_e2e):
it monitors every lifecycle transition on disk. The live run only adds "real Claude Code
hooks/MCP/recall actually fire".
"""
import json

import pytest

from autoharness import config
from autoharness.hook import capture, dispatch, spawn
from autoharness.lib import counters, intent_queue, layer, ledger, sidecar, skill_store

LEARNED = "---\nname: learned\ndescription: Does a specific repeatable thing.\n---\n# Learned\nSteps.\n"
WEAK = "---\nname: weak\ndescription: Rarely useful side note.\n---\n# Weak\nx.\n"


@pytest.fixture(autouse=True)
def _small_isolated(monkeypatch):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    monkeypatch.setattr(config, "REFLECT_EVERY_N", 2)
    monkeypatch.setattr(config, "MATURITY_THRESHOLD", {layer.GLOBAL: 2, layer.PROJECT: 2})
    monkeypatch.setattr(config, "CAPACITY", {layer.GLOBAL: 5, layer.PROJECT: 1})


def _roots(tmp_path):
    return {layer.GLOBAL: tmp_path / "g", layer.PROJECT: tmp_path / "p"}


def _transcript(tmp_path):
    p = tmp_path / "transcript.jsonl"
    lines = []
    for i in range(4):
        lines.append(json.dumps({"type": "user", "message": {"role": "user", "content": f"q{i}"}}))
        lines.append(json.dumps({"type": "assistant", "message": {"role": "assistant", "content": f"a{i}"}}))
    p.write_text("\n".join(lines) + "\n")
    return p


def test_full_skill_lifecycle_through_dispatch(tmp_path, capsys):
    roots = _roots(tmp_path)
    proot = roots[layer.PROJECT]
    transcript = _transcript(tmp_path)
    stop = {"hook_event_name": "Stop", "session_id": "s1", "transcript_path": str(transcript)}

    def land_learned(event, result, rts):  # stands in for the spawned reflector
        def fake_spawn(argv, env, bundle):
            intent_queue.append(env[config.RUN_ID_ENV],
                                {"action": "create", "name": "learned", "level": "project",
                                 "body": LEARNED, "reason": "captured repeat", "evidence": "slice"},
                                rts[layer.PROJECT])
        spawn.run(capture.window(event["transcript_path"], result["window_n"]),
                  dispatch._run_id(result), roots=rts, spawn_fn=fake_spawn)

    # BEAT 1 — birth: drive Stops until the cadence triggers reflection
    dispatch.dispatch(stop, roots=roots, reflect=land_learned)            # Stop 1: count<N, no trigger
    assert skill_store.read_body("project", "learned", proot) is None
    dispatch.dispatch(stop, roots=roots, reflect=land_learned)            # Stop 2: trigger → land
    assert skill_store.read_body("project", "learned", proot) is not None
    assert sidecar.is_agent_created("project", "learned", proot)
    assert ledger.read("project", "learned", proot)[0]["action"] == "create"
    assert counters.request_count(layer.PROJECT, proot) == 2              # denominator grew per Stop
    print(f"[birth]  learned landed · denominator={counters.request_count(layer.PROJECT, proot)}")

    # BEAT 2 — use: PreToolUse(Skill) bumps the numerator
    for _ in range(2):
        dispatch.dispatch({"hook_event_name": "PreToolUse", "tool_name": "Skill",
                           "tool_input": {"name": "learned"}}, roots=roots)
    assert sidecar.read("project", "learned", proot)["calls"] == 2
    print(f"[use]    learned calls={sidecar.read('project', 'learned', proot)['calls']}")

    # BEAT 3 — compete: a weak unused peer; MNG recompute (SessionStart) archives the loser.
    skill_store.write_body("project", "weak", WEAK, proot)
    sidecar.create("project", "weak", anchor=0, root=proot)              # mature (denom 2), zero calls
    req = counters.request_count(layer.PROJECT, proot)
    mat = config.MATURITY_THRESHOLD[layer.PROJECT]
    for name in ("learned", "weak"):                                    # monitor MNG numerator/denominator
        sc = sidecar.read("project", name, proot)
        num, den = sc["calls"], req - sc["anchor"]
        print(f"[mng]    {name}: numerator(calls)={num} denominator(reqs)={den} "
              f"rate={num / den:.2f} mature={den >= mat}")
    out = dispatch.dispatch({"hook_event_name": "SessionStart"}, roots=roots)
    archived = out["result"]["archived"]["project"]
    assert "weak" in archived and "learned" not in archived            # lowest rate sheds, adhered-to kept
    assert not skill_store.exists("project", "weak", proot)             # moved out of live tree
    assert (layer.archive_dir("project", proot) / "weak").exists()
    assert skill_store.exists("project", "learned", proot)
    print(f"[archive] capacity={config.CAPACITY[layer.PROJECT]} → archived={archived} · learned survives")

    # BEAT 4 — restore: archival is reversible
    skill_store.restore("project", "weak", proot)
    assert skill_store.exists("project", "weak", proot)
    print("[restore] weak reactivated")
