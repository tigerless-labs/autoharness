import pytest

from autoharness import config

_OPERATOR_ENV = ("AUTOHARNESS_PROJECT_DIR", "AUTOHARNESS_GLOBAL_DIR", "AUTOHARNESS_STATE_HOME",
                 "CLAUDE_CONFIG_DIR")


@pytest.fixture(autouse=True)
def _host_defaults(monkeypatch):
    """Every test starts from the plugin's defaults, whatever the developer's shell exports."""
    for name in _OPERATOR_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(config, "SKILL_PREFIX", "")
    monkeypatch.setattr(config, "CHILD_ISOLATION", False)
