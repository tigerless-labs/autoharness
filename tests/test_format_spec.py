from autoharness import config


def test_format_spec_exists_and_states_required_fields():
    assert config.FORMAT_SPEC.is_file()
    text = config.FORMAT_SPEC.read_text()
    assert text.strip()
    # 必填字段名是 #416 linter 与 reflector authoring 的同源契约 —— 不写到就会漂移
    for token in ["name", "description", "global"]:
        assert token in text


def test_redaction_rules_exists():
    assert config.REDACTION_RULES.is_file()
