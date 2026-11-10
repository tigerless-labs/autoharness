from autoharness import config
from autoharness.hook import dispatch
from autoharness.lib import counters


def test_failed_reflector_launch_does_not_skip_periodic_curator(tmp_path, monkeypatch):
    monkeypatch.delenv(config.CHILD_SESSION_ENV, raising=False)
    monkeypatch.setattr(config, 'CONSOLIDATE_EVERY_N', 1)
    monkeypatch.setattr(config, 'REFLECT_EVERY_N', 1)
    roots = {'project': tmp_path / 'p', 'global': tmp_path / 'g'}
    counters.bump_session('s1', roots['project'])
    curations = []
    result = dispatch.dispatch({'hook_event_name': 'Stop', 'session_id': 's1', 'transcript_path': 'owned.jsonl'}, roots=roots,
       reflect=lambda *args: {'error': 'owned launch failed'}, consolidate=lambda run_id, roots: curations.append(run_id))
    assert result['error'] == 'owned launch failed'
    assert curations == ['s1-c1']
