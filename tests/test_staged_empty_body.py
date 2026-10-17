import pytest

from autoharness.lib import intent_queue
from autoharness.stage_skill import server


@pytest.mark.parametrize('action', ['create', 'update'])
def test_stage_rejects_frontmatter_only_before_queueing(tmp_path, action):
    body = '---\nname: foo\ndescription: Use when formatting dates.\n---\n\n'
    params = {'action': action, 'name': 'foo', 'reason': 'observed reuse', 'evidence': 'fixture evidence', 'body': body}
    result = server.stage(params, run_id='owned', root=tmp_path)
    assert not result['ok']
    assert any(family == 'completeness' for family, detail in result['errors'])
    assert intent_queue.read('owned', tmp_path) == []
    assert server.stage({**params, 'body': body + 'Use strftime.\n'}, run_id='owned', root=tmp_path)['ok']
