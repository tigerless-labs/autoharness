import pytest

from autoharness import config
from autoharness.hook import dispatch
from autoharness.lib import counters, sidecar, skill_store


@pytest.mark.parametrize('agent', ['other-plugin:curator', 'other-plugin:reflector'])
def test_foreign_plugin_agent_is_not_our_maintenance_agent(tmp_path, monkeypatch, agent):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    roots = {'project': tmp_path / 'p', 'global': tmp_path / 'g'}
    verdict = dispatch.dispatch({'hook_event_name': 'PreToolUse', 'agent_type': agent, 'session_id': 'foreign', 'tool_name': 'Write'}, roots=roots)
    assert not verdict.get('deny')
    assert counters.session_count('foreign', roots['project']) == 1


@pytest.mark.parametrize('tool', ['Read', 'Skill'])
def test_own_reflector_never_counts_usage_or_activity(tmp_path, monkeypatch, tool):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    roots = {'project': tmp_path / 'p', 'global': tmp_path / 'g'}
    skill_store.write_body('project', 'owned', 'body', roots['project'])
    sidecar.create('project', 'owned', 0, roots['project'])
    event = {'hook_event_name': 'PreToolUse', 'agent_type': config.REFLECTOR_AGENT, 'session_id': 'child', 'tool_name': tool,
             'tool_input': {'skill': 'owned', 'file_path': str(roots['project'] / 'skills/owned/SKILL.md')}}
    assert not dispatch.dispatch(event, roots=roots)['result']['counted']
    assert counters.session_count('child', roots['project']) == 0
    card = sidecar.read('project', 'owned', roots['project'])
    assert card['use'] == card['view'] == 0
