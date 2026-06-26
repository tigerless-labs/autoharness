from autoharness import config
from autoharness.lib import layer


def test_cadence_positive():
    assert isinstance(config.REFLECT_EVERY_N, int) and config.REFLECT_EVERY_N > 0


def test_layered_knobs_cover_both_layers_and_positive():
    for knob in (config.MATURITY_THRESHOLD, config.CAPACITY):
        assert set(knob) == set(layer.LAYERS)
        assert all(isinstance(v, int) and v > 0 for v in knob.values())


def test_contract_data_pointers_named_in_lib():
    assert config.REDACTION_RULES.name == "redaction_rules.toml"
    assert config.FORMAT_SPEC.name == "format_spec.md"
    assert config.REDACTION_RULES.parent == config.FORMAT_SPEC.parent


def test_spawn_pointers_present_and_distinct():
    assert config.REFLECTOR_AGENT and isinstance(config.REFLECTOR_AGENT, str)
    assert config.CLAUDE_BIN and isinstance(config.CLAUDE_BIN, str)
    envs = {config.RUN_ID_ENV, config.PROJECT_ROOT_ENV, config.CHILD_SESSION_ENV}
    assert len(envs) == 3 and all(e and isinstance(e, str) for e in envs)
