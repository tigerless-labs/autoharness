"""Punctuation must not turn a usable carried script into a missing path."""
import subprocess

import pytest

from autoharness.hook import promoter
from autoharness.lib import sidecar, skill_store
from autoharness.stage_skill import server

BODY = "---\nname: run\ndescription: Use when formatting a date as ISO.\n---\n# Run\nRun {pointer}\n"
SCRIPT = "printf 'ok\\n'\n"


@pytest.mark.parametrize("pointer", ["scripts/run.sh.", "./scripts/run.sh.", "scripts/run.sh...", "`scripts/run.sh`."])
def test_sentence_reference_lands_and_script_remains_usable(tmp_path, pointer):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    staged = server.stage({
        "action": "create", "name": "run", "body": BODY.format(pointer=pointer),
        "files": {"scripts/run.sh": SCRIPT}, "reason": "supported script reference",
        "evidence": "local fixture",
    }, run_id="sentence", root=tmp_path)
    assert staged["ok"]
    verdicts = promoter.drain("sentence", roots=roots)
    assert verdicts[0]["ok"], verdicts
    script = skill_store.skill_path("project", "run", tmp_path).parent / "scripts/run.sh"
    result = subprocess.run(["/bin/sh", str(script)], capture_output=True, text=True,
                            encoding="utf-8", timeout=5, check=True)
    assert result.stdout == "ok\n"


def test_a_real_legacy_trailing_period_filename_remains_referenced(tmp_path):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    skill_store.write_body("project", "run", BODY.format(pointer="`scripts/run.sh.`"), tmp_path)
    sidecar.create("project", "run", 0, tmp_path)
    directory = skill_store.skill_path("project", "run", tmp_path).parent / "scripts"
    directory.mkdir()
    (directory / "run.sh.").write_text(SCRIPT, encoding="utf-8")
    verdict = promoter.promote({
        "action": "update", "name": "run", "body": BODY.format(pointer="scripts/run.sh."),
        "reason": "retain an existing supported filename", "evidence": "local fixture",
    }, roots=roots)
    assert verdict["ok"], verdict
    assert not (directory / "run.sh").exists()


def test_longer_unknown_pointer_does_not_match_the_carried_prefix(tmp_path):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    staged = server.stage({
        "action": "create", "name": "run", "body": BODY.format(pointer="scripts/run.sh.bak."),
        "files": {"scripts/run.sh": SCRIPT}, "reason": "negative control", "evidence": "local fixture",
    }, run_id="unknown", root=tmp_path)
    # the exact-pointer check rejects the longer filename already at stage time; if a stage ever
    # lets it through, the promoter must still reject it
    if staged["ok"]:
        findings = promoter.drain("unknown", roots=roots)[0]["findings"]
    else:
        findings = staged["errors"]
    assert any(kind == "structure" for kind, _ in findings)
    assert not skill_store.skill_path("project", "run", tmp_path).exists()


@pytest.mark.parametrize("pointer", ["`scripts/run.sh.`", "``scripts/run.sh.``", "`Run scripts/run.sh. now`"])
def test_a_period_inside_a_code_span_denotes_the_actual_filename(tmp_path, pointer):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    staged = server.stage({
        "action": "create", "name": "run", "body": BODY.format(pointer=pointer),
        "files": {"scripts/run.sh": SCRIPT}, "reason": "explicit filename negative control",
        "evidence": "local fixture",
    }, run_id="literal", root=tmp_path)
    assert staged["ok"]
    verdicts = promoter.drain("literal", roots=roots)
    assert not verdicts[0]["ok"]
    assert any("scripts/run.sh." in text for kind, text in verdicts[0]["findings"] if kind == "structure")
    assert not skill_store.skill_path("project", "run", tmp_path).exists()


@pytest.mark.parametrize("pointer", ["scripts/run.sh.", "./scripts/run.sh.", "scripts/run.sh...", "`scripts/run.sh`."])
def test_staged_removal_requires_patching_out_sentence_pointer(tmp_path, pointer):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    body = BODY.format(pointer=pointer)
    create = {"action": "create", "name": "run", "body": body,
              "files": {"scripts/run.sh": SCRIPT}, "reason": "create helper", "evidence": "fixture"}
    assert server.stage(create, run_id="create", root=tmp_path)["ok"]
    assert promoter.drain("create", roots=roots)[0]["ok"]
    script = skill_store.skill_path("project", "run", tmp_path).parent / "scripts/run.sh"
    remove = {"action": "remove_file", "name": "run", "path": "scripts/run.sh",
              "reason": "drop helper", "evidence": "fixture"}
    assert server.stage(remove, run_id="remove", root=tmp_path)["ok"]
    verdict = promoter.drain("remove", roots=roots)[0]
    assert not verdict["ok"], verdict
    assert script.read_text(encoding="utf-8") == SCRIPT
    assert skill_store.read_body("project", "run", tmp_path) == body
    patch = {"action": "patch", "name": "run", "old_string": "Run " + pointer,
             "new_string": "Use strftime.", "reason": "retire pointer", "evidence": "fixture"}
    assert server.stage(patch, run_id="patch", root=tmp_path)["ok"]
    assert promoter.drain("patch", roots=roots)[0]["ok"]
    assert server.stage(remove, run_id="remove-after", root=tmp_path)["ok"]
    assert promoter.drain("remove-after", roots=roots)[0]["ok"]
    assert not script.exists()


@pytest.mark.parametrize("pointer", ["scripts/run.sh.", "`scripts/run.sh.`", "scripts/run.sh.bak"])
def test_removal_respects_exact_other_filename(tmp_path, pointer):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    skill_store.write_body("project", "run", BODY.format(pointer=pointer), tmp_path)
    sidecar.create("project", "run", 0, tmp_path)
    directory = skill_store.skill_path("project", "run", tmp_path).parent / "scripts"
    directory.mkdir()
    (directory / "run.sh").write_text(SCRIPT, encoding="utf-8")
    (directory / "run.sh.").write_text(SCRIPT, encoding="utf-8")
    (directory / "run.sh.bak").write_text(SCRIPT, encoding="utf-8")
    remove = {"action": "remove_file", "name": "run", "path": "scripts/run.sh",
              "reason": "drop unreferenced helper", "evidence": "fixture"}
    assert server.stage(remove, run_id="remove-other", root=tmp_path)["ok"]
    assert promoter.drain("remove-other", roots=roots)[0]["ok"]
    assert not (directory / "run.sh").exists()
    assert (directory / "run.sh.").exists()
    assert (directory / "run.sh.bak").exists()


def test_removal_blocks_referenced_legacy_period_filename(tmp_path):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    skill_store.write_body("project", "run", BODY.format(pointer="`scripts/run.sh.`"), tmp_path)
    sidecar.create("project", "run", 0, tmp_path)
    directory = skill_store.skill_path("project", "run", tmp_path).parent / "scripts"
    directory.mkdir()
    script = directory / "run.sh."
    script.write_text(SCRIPT, encoding="utf-8")
    remove = {"action": "remove_file", "name": "run", "path": "scripts/run.sh.",
              "reason": "drop helper", "evidence": "fixture"}
    assert server.stage(remove, run_id="legacy-remove", root=tmp_path)["ok"]
    assert not promoter.drain("legacy-remove", roots=roots)[0]["ok"]
    assert script.exists()


@pytest.mark.parametrize("pointer", ["https://example.test/scripts/run.sh", "foo/scripts/run.sh"])
def test_external_or_nested_prefix_does_not_block_local_removal(tmp_path, pointer):
    roots = {"project": tmp_path, "global": tmp_path / "unused"}
    skill_store.write_body("project", "run", BODY.format(pointer=pointer), tmp_path)
    sidecar.create("project", "run", 0, tmp_path)
    directory = skill_store.skill_path("project", "run", tmp_path).parent / "scripts"
    directory.mkdir()
    script = directory / "run.sh"
    script.write_text(SCRIPT, encoding="utf-8")
    update = {"action": "update", "name": "run", "body": BODY.format(pointer=pointer),
              "reason": "retain external example", "evidence": "fixture"}
    assert server.stage(update, run_id="external-update", root=tmp_path)["ok"]
    assert promoter.drain("external-update", roots=roots)[0]["ok"]
    remove = {"action": "remove_file", "name": "run", "path": "scripts/run.sh",
              "reason": "remove unrelated local helper", "evidence": "fixture"}
    assert server.stage(remove, run_id="external-remove", root=tmp_path)["ok"]
    assert promoter.drain("external-remove", roots=roots)[0]["ok"]
    assert not script.exists()
