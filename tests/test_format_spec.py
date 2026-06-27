from autoharness import config


def test_format_spec_exists_and_states_required_fields():
    assert config.FORMAT_SPEC.is_file()
    text = config.FORMAT_SPEC.read_text()
    assert text.strip()
    # required field names are the shared contract between the #416 linter and reflector authoring -- omit one and they drift
    for token in ["name", "description", "global"]:
        assert token in text


def test_redaction_rules_exists():
    assert config.REDACTION_RULES.is_file()
