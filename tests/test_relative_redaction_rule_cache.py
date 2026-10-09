from autoharness.lib import redact


def test_relative_rule_paths_are_resolved_in_the_current_directory(
    tmp_path, monkeypatch
):
    redact._rules.cache_clear()
    try:
        for label in ["first", "second"]:
            directory = tmp_path / label
            directory.mkdir()
            (directory / "rules.toml").write_text(
                f'[[pii]]\nname = "{label}"\npattern = "fixture"\n'
            )
            monkeypatch.chdir(directory)
            assert redact.redact("fixture", "rules.toml") == f"[REDACTED:pii:{label}]"
    finally:
        redact._rules.cache_clear()
