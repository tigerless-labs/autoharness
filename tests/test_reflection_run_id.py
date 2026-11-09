import re

from autoharness.hook import dispatch


def test_repeated_cadence_has_distinct_queue_and_account_names(tmp_path):
    result = {"session_id": "same-session", "count": 10}
    launches = []
    roots = {"project": tmp_path / "p", "global": tmp_path / "g"}
    for _ in range(3):
        dispatch._reflect(
            {"transcript_path": "unused.jsonl"},
            result,
            roots,
            launch=lambda *args: launches.append(args),
        )
    run_ids = [args[2] for args in launches]
    assert len(set(run_ids)) == 3
    assert all(re.fullmatch(r"same-session-10-[a-f0-9]{32}", rid) for rid in run_ids)
