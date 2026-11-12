import json

from autoharness import config
from autoharness.hook import dedupe_index, spawn
from autoharness.lib import layer, skill_store

GOOD = "---\nname: {name}\ndescription: {description}\n---\n# body\n"


def _roots(tmp_path):
    return {layer.GLOBAL: tmp_path / "global", layer.PROJECT: tmp_path / "repo" / ".claude"}


def _skill(path, name, description):
    path.mkdir(parents=True)
    (path / "SKILL.md").write_text(
        GOOD.format(name=name, description=description), encoding="utf-8"
    )


def test_indexes_archived_skills_as_read_only(tmp_path):
    roots = _roots(tmp_path)
    skill_store.write_body(
        "project", "old-deploy",
        GOOD.format(name="old-deploy", description="Use when deploying the service"),
        roots["project"],
    )
    skill_store.archive("project", "old-deploy", roots["project"])

    index = dedupe_index.read_only_index(roots)

    assert '"owner": "archived:project"' in index
    assert '"name": "old-deploy"' in index
    assert "not recreated under a new name" in index


def test_indexes_archive_when_state_is_redirected(tmp_path, monkeypatch):
    roots = _roots(tmp_path)
    monkeypatch.setenv("AUTOHARNESS_STATE_HOME", str(tmp_path / "state"))
    skill_store.write_body(
        "project", "old-test",
        GOOD.format(name="old-test", description="Use when running the old test suite"),
        roots["project"],
    )
    skill_store.archive("project", "old-test", roots["project"])

    index = dedupe_index.read_only_index(roots)

    assert '"owner": "archived:project"' in index
    assert "running the old test suite" in index


def test_indexes_current_plugin_version_from_install_registry(tmp_path):
    roots = _roots(tmp_path)
    plugins = roots["global"] / "plugins"
    current = plugins / "cache" / "market" / "toolkit" / "2.0.0"
    stale = plugins / "cache" / "market" / "toolkit" / "1.0.0"
    _skill(current / "skills" / "deploy", "deploy", "Use when deploying widgets")
    _skill(stale / "skills" / "old", "old", "stale plugin skill")
    plugins.mkdir(parents=True, exist_ok=True)
    (plugins / "installed_plugins.json").write_text(json.dumps({
        "version": 2,
        "plugins": {
            "toolkit@market": [{
                "scope": "user", "version": "2.0.0", "installPath": str(current)
            }]
        },
    }), encoding="utf-8")

    index = dedupe_index.read_only_index(roots)

    assert '"owner": "plugin:toolkit@market"' in index
    assert "Use when deploying widgets" in index
    assert "stale plugin skill" not in index


def test_plugin_cache_fallback_skips_orphaned_version(tmp_path):
    roots = _roots(tmp_path)
    plugins = roots["global"] / "plugins"
    current = plugins / "cache" / "market" / "toolkit" / "2.0.0"
    orphan = plugins / "cache" / "market" / "toolkit" / "3.0.0"
    _skill(current / "skills" / "deploy", "deploy", "current fallback")
    _skill(orphan / "skills" / "future", "future", "orphaned fallback")
    (orphan / ".orphaned_at").write_text("now", encoding="utf-8")

    index = dedupe_index.read_only_index(roots)

    assert "current fallback" in index
    assert "orphaned fallback" not in index


def test_indexes_scheduled_tasks_and_instruction_files(tmp_path):
    roots = _roots(tmp_path)
    _skill(
        roots["global"] / "scheduled-tasks" / "nightly",
        "nightly-maintenance",
        "Use when running nightly maintenance",
    )
    user_rules = roots["global"] / "CLAUDE.md"
    project_rules = roots["project"].parent / "CLAUDE.md"
    user_rules.parent.mkdir(parents=True, exist_ok=True)
    project_rules.parent.mkdir(parents=True, exist_ok=True)
    user_rules.write_text("always use uv", encoding="utf-8")
    project_rules.write_text("deploy with make release", encoding="utf-8")

    index = dedupe_index.read_only_index(roots)

    assert '"owner": "scheduled-task"' in index
    assert "nightly-maintenance" in index
    assert str(user_rules) in index and str(project_rules) in index
    assert "always use uv" in index and "deploy with make release" in index
    assert index.count('"owner": "claude-md"') == 2


def test_indexes_only_current_projects_auto_memory(tmp_path):
    roots = _roots(tmp_path)
    transcript = tmp_path / "config" / "projects" / "repo-key" / "session.jsonl"
    memory = transcript.parent / "memory" / "MEMORY.md"
    memory.parent.mkdir(parents=True)
    memory.write_text("- [deploy](deploy.md): release procedure\n", encoding="utf-8")
    other = transcript.parent.parent / "other" / "memory" / "MEMORY.md"
    other.parent.mkdir(parents=True)
    other.write_text("OTHER PROJECT SECRET", encoding="utf-8")

    index = dedupe_index.read_only_index(roots, transcript_path=transcript)

    assert '"owner": "auto-memory"' in index
    assert "release procedure" in index
    assert str(memory) in index
    assert "OTHER PROJECT SECRET" not in index


def test_malformed_or_unreadable_sources_fail_open(tmp_path):
    roots = _roots(tmp_path)
    plugins = roots["global"] / "plugins"
    plugins.mkdir(parents=True)
    (plugins / "installed_plugins.json").write_text("{not json", encoding="utf-8")
    bad = roots["global"] / "scheduled-tasks" / "bad"
    bad.mkdir(parents=True)
    (bad / "SKILL.md").write_bytes(b"\xff\xfe")

    assert dedupe_index.read_only_index(roots) == ""


def test_global_disable_excludes_global_read_only_sources(tmp_path, monkeypatch):
    roots = _roots(tmp_path)
    _skill(
        roots["global"] / "scheduled-tasks" / "nightly",
        "nightly",
        "global task",
    )
    project_rules = roots["project"].parent / "CLAUDE.md"
    project_rules.parent.mkdir(parents=True, exist_ok=True)
    project_rules.write_text("project rule", encoding="utf-8")
    monkeypatch.setattr(config, "DISABLE_GLOBAL", True)

    index = dedupe_index.read_only_index(roots)

    assert "global task" not in index
    assert str(project_rules) in index


def test_reflector_gets_read_only_sources_but_curator_does_not(tmp_path):
    roots = _roots(tmp_path)
    _skill(
        roots["global"] / "scheduled-tasks" / "nightly",
        "nightly",
        "Use when doing nightly work",
    )

    reflector = spawn.reflector_index(roots)
    curator = spawn.description_index(roots, agent_only=True)

    assert dedupe_index.READ_ONLY_HEADER in reflector
    assert "nightly work" in reflector
    assert dedupe_index.READ_ONLY_HEADER not in curator
    assert "nightly work" not in curator


def test_run_passes_transcript_memory_into_reflector_bundle(tmp_path):
    roots = _roots(tmp_path)
    transcript = tmp_path / "projects" / "repo" / "session.jsonl"
    memory = transcript.parent / "memory" / "MEMORY.md"
    memory.parent.mkdir(parents=True)
    memory.write_text("- test command is make check\n", encoding="utf-8")
    seen = {}

    spawn.run(
        "WINDOW", "run-1", roots=roots, transcript_path=transcript,
        spawn_fn=lambda argv, env, payload: seen.update(payload=payload),
    )

    assert "test command is make check" in seen["payload"]
    assert "# Existing skills" in seen["payload"]
