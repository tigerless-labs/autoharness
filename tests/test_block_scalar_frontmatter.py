"""Expected string values follow YAML block scalar indentation, folding and chomping."""
import pytest

from autoharness.hook import on_session_start, promoter
from autoharness.lib import validate
from autoharness.stage_skill import server


@pytest.mark.parametrize("header,content,expected", [
    ("|-", "  first\n  second", "first\nsecond"),
    ("|", "  first\n  second", "first\nsecond\n"),
    ("|+", "  first\n\n", "first\n\n\n"),
    (">-", "  first\n  second", "first second"),
    (">", "  first\n  second", "first second\n"),
    (">+", "  first\n\n", "first\n\n\n"),
    (">-", "  first\n\n  second", "first\nsecond"),
    (">-", "\n  first", "\nfirst"),
    (">-", "  first\n    indented\n  last", "first\n  indented\nlast"),
    ("|2-", "    first\n  last", "  first\nlast"),
    (">-2", "    first\n  last", "  first\nlast"),
    (">2- # note", "  first\n  next: value", "first next: value"),
    ("|-", "  # literal content", "# literal content"),
    ("|-", "  \t\n  text", "\t\ntext"),
    ("|-", "  \u00a0\n  text", "\u00a0\ntext"),
    ("|-", "  first\n # trailing comment", "first"),
    (">+", "  first\n\n # trailing comment\n    # later comment", "first\n\n"),
    (">-", "", ""),
    ("|", "\n", ""),
    ("|+", "\n", "\n\n"),
])
def test_decoded_block_string(header, content, expected):
    body = f"---\nname: sample\ndescription: {header}\n{content}\ncategory: dates\n---\n# Body\nText.\n"
    actual = validate._frontmatter(body)
    assert actual["description"] == expected
    assert actual["category"] == "dates"
    assert set(actual) == {"name", "description", "category"}


@pytest.mark.parametrize("content", ["    \n  text", "  first\n second"])
def test_invalid_detected_block_indentation_is_not_admitted(content):
    body = f"---\nname: sample\ndescription: >-\n{content}\n---\n# Body\nText.\n"
    assert validate._frontmatter(body) is None


@pytest.mark.parametrize("description", ["Use when formatting dates.", "'Use when formatting dates.'", '"Use when formatting dates."'])
def test_existing_single_line_formats_remain_unchanged(description):
    body = f"---\nname: sample\ndescription: {description}\n---\n# Body\nText.\n"
    assert validate._frontmatter(body)["description"] == "Use when formatting dates."


@pytest.mark.parametrize("literal", ["'|-'", '">-"'])
def test_quoted_indicators_are_literal_strings(literal):
    body = f"---\nname: sample\ndescription: {literal}\n---\n# Body\nText.\n"
    assert validate._frontmatter(body)["description"] == literal[1:-1]


@pytest.mark.parametrize("header", [">-", "|-", ">", "|", ">2-"])
def test_stage_drain_and_recall_use_the_decoded_description(tmp_path, header):
    body = ("---\nname: iso\ndescription: " + header
            + "\n  Use when formatting a date\n  as ISO.\n---\n# ISO\nUse strftime.\n")
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    staged = server.stage({"action": "create", "name": "iso", "body": body,
                           "reason": "supported YAML description", "evidence": "local fixture"},
                          run_id="block", root=tmp_path)
    assert staged["ok"], staged
    verdicts = promoter.drain("block", roots=roots)
    assert verdicts[0]["ok"], verdicts
    actual_context = on_session_start.on_session_start({"cwd": str(tmp_path)}, roots=roots)["context"]
    assert "Use when formatting a date as ISO." in actual_context
    assert ": >" not in actual_context and ": |" not in actual_context
