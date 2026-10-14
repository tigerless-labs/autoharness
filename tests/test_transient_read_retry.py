from pathlib import Path

import pytest

from autoharness.hook import promoter
from autoharness.lib import intent_queue, sidecar, skill_store


def test_transient_read_failure_preserves_intent_for_retry(tmp_path, monkeypatch):
    roots = {'project': tmp_path / 'p', 'global': tmp_path / 'g'}
    body = '---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n'
    skill_store.write_body('project', 'foo', body, roots['project'])
    sidecar.create('project', 'foo', 0, roots['project'])
    helper = roots['project'] / 'skills/foo/helper.py'
    helper.write_text("print('fixture')\n")
    intent_queue.append('owned', {'action': 'update', 'name': 'foo', 'body': body + 'See helper.py.\n', 'reason': 'observed reuse', 'evidence': 'fixture evidence'}, roots['project'])
    original = Path.read_text
    def unreadable(path, *args, **kwargs):
        if path == helper:
            raise PermissionError('owned transient read denied')
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', unreadable)
    with pytest.raises(PermissionError):
        promoter.drain('owned', roots=roots)
    assert len(intent_queue.read('owned', roots['project'])) == 1
    monkeypatch.setattr(Path, 'read_text', original)
    result = promoter.drain('owned', roots=roots)
    assert result[0]['ok'], result
    assert intent_queue.read('owned', roots['project']) == []
