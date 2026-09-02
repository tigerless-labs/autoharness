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
    # description-as-trigger is shared contract between validate's cue/budget checks and reflector authoring
    for token in ["trigger", "use when", "INDEX_DESC_MAX_CHARS"]:
        assert token.lower() in text.lower()


def test_format_spec_states_category_field():
    text = config.FORMAT_SPEC.read_text()
    # category is validated frontmatter and the grouping key of the self-injected recall index;
    # unstated here, REF never emits it and every skill collapses into one group
    for token in ["category", "INDEX_DESC_MAX_CHARS"]:
        assert token in text


def test_format_spec_states_the_one_sentence_rule():
    text = config.FORMAT_SPEC.read_text()
    # adopted from hermes: the description IS the index line, so the rule is one sentence inside the
    # budget with the trigger first — the old four-element recipe produced 385-char descriptions that
    # the index cut mid-clause (E11, first real replay)
    for token in ["one sentence", "trigger first", "words a", "body"]:
        assert token in text
