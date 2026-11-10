"""Regression: _PLACEHOLDER must not match legitimate markdown callout tags."""
from autoharness.lib.validate import _PLACEHOLDER


def test_placeholder_still_catches_real_placeholders():
    """Known placeholder tags are still detected."""
    for tag in ["<TODO>", "<FIXME>", "<PLACEHOLDER>", "<TBD>", "<REPLACE_ME>", "<INSERT_HERE>"]:
        assert _PLACEHOLDER.search(f"fill in {tag} later"), f"should match {tag}"


def test_placeholder_ignores_markdown_callouts():
    """Legitimate markdown callout tags must not trigger the completeness check."""
    for tag in ["<NOTE>", "<IMPORTANT>", "<WARNING>", "<EXAMPLE>", "<CAUTION>", "<TIP>"]:
        assert not _PLACEHOLDER.search(f"see {tag} for details"), f"should NOT match {tag}"


def test_placeholder_still_catches_todo_fixme_colon():
    """The TODO:/FIXME:/XXX: prefix form still works."""
    assert _PLACEHOLDER.search("TODO: implement this")
    assert _PLACEHOLDER.search("FIXME: broken")
    assert _PLACEHOLDER.search("XXX: needs review")
