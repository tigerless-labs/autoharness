import importlib

from autoharness import config
from autoharness.lib import layer


def test_cadence_positive():
    assert isinstance(config.REFLECT_EVERY_N, int) and config.REFLECT_EVERY_N > 0


def test_consolidate_cadence_sparser_than_reflect():
    # curation runs periodically like reflection but rarer — merging the library is a coarser beat
    assert isinstance(config.CONSOLIDATE_EVERY_N, int)
    assert config.CONSOLIDATE_EVERY_N > config.REFLECT_EVERY_N


def test_curator_agent_named_and_distinct():
    assert config.CURATOR_AGENT and isinstance(config.CURATOR_AGENT, str)
    assert config.CURATOR_AGENT != config.REFLECTOR_AGENT


def test_env_overrides_consolidate_cadence(monkeypatch):
    monkeypatch.setenv("AUTOHARNESS_CONSOLIDATE_EVERY_N", "7")
    importlib.reload(config)
    try:
        assert config.CONSOLIDATE_EVERY_N == 7
    finally:
        monkeypatch.undo()
        importlib.reload(config)


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


def test_env_overrides_knobs_else_defaults(monkeypatch):
    monkeypatch.setenv("AUTOHARNESS_REFLECT_EVERY_N", "2")
    monkeypatch.setenv("AUTOHARNESS_MATURITY_PROJECT", "3")
    monkeypatch.setenv("AUTOHARNESS_CAPACITY_PROJECT", "1")
    importlib.reload(config)
    try:
        assert config.REFLECT_EVERY_N == 2
        assert config.MATURITY_THRESHOLD[layer.PROJECT] == 3
        assert config.CAPACITY[layer.PROJECT] == 1
        assert config.CAPACITY[layer.GLOBAL] == 20  # unset → default preserved
    finally:
        monkeypatch.undo()
        importlib.reload(config)  # restore defaults for the rest of the suite
