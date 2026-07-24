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


def test_format_spec_states_subfile_contract():
    text = config.FORMAT_SPEC.read_text()
    # subfile categories + the pointer rule are shared contract between validate and reflector authoring
    for token in ["scripts/", "templates/", "assets/", "references/", "Pointer rule"]:
        assert token in text


def test_format_spec_states_altitude_cap():
    text = config.FORMAT_SPEC.read_text()
    # altitude rule is shared contract between validate's line cap and reflector authoring
    for token in ["Altitude", "SKILL_BODY_MAX_LINES"]:
        assert token in text


def test_format_spec_states_description_trigger_contract():
    text = config.FORMAT_SPEC.read_text()
    # description-as-trigger is shared contract between validate's cue/length checks and reflector authoring
    for token in ["trigger", "use when", "SKILL_DESC_MAX_CHARS"]:
        assert token in text
