import hashlib

from autoharness.hook import promoter
from autoharness.lib import layer


def test_distinct_evidence_with_equal_short_hashes_stays_distinct(tmp_path):
    first = "Fixture observation 0x2849"
    second = "Fixture observation 0x8362"
    assert (
        hashlib.sha256(first.encode()).hexdigest()[:8]
        == hashlib.sha256(second.encode()).hexdigest()[:8]
    )
    first_ref = promoter._materialize_evidence("project", "foo", first, tmp_path)
    second_ref = promoter._materialize_evidence("project", "foo", second, tmp_path)
    assert first_ref != second_ref
    assert (
        layer.subfile_path("project", "foo", first_ref, tmp_path).read_text() == first
    )
    assert (
        layer.subfile_path("project", "foo", second_ref, tmp_path).read_text() == second
    )
    assert (
        promoter._materialize_evidence("project", "foo", first, tmp_path) == first_ref
    )
