from autoharness.lib import ledger


def test_append_only_grows_and_never_mutates(tmp_path):
    ledger.append("project", "foo", {"action": "create", "reason": "r1"}, tmp_path)
    ledger.append("project", "foo", {"action": "patch", "reason": "r2"}, tmp_path)
    rows = ledger.read("project", "foo", tmp_path)
    assert [r["action"] for r in rows] == ["create", "patch"]

    ledger.append("project", "foo", {"action": "delete", "reason": "r3"}, tmp_path)
    rows2 = ledger.read("project", "foo", tmp_path)
    assert rows2[:2] == rows  # existing entries only grow, never mutate
    assert len(rows2) == 3


def test_missing_ledger_reads_empty(tmp_path):
    assert ledger.read("project", "none", tmp_path) == []


def test_two_symbols_isolated(tmp_path):
    ledger.append("project", "a", {"action": "create"}, tmp_path)
    ledger.append("project", "b", {"action": "create"}, tmp_path)
    ledger.append("project", "a", {"action": "patch"}, tmp_path)
    assert len(ledger.read("project", "a", tmp_path)) == 2
    assert len(ledger.read("project", "b", tmp_path)) == 1
