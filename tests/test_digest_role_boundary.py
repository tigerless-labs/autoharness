import json

from autoharness.hook import capture


def test_review_digest_keeps_role_label_after_window_truncation(tmp_path):
    path = tmp_path / 'transcript.jsonl'
    path.write_text('\n'.join(json.dumps({'type': 'user', 'message': {'content': f'line-{i:03} ' + 'x' * 18}}) for i in range(60)))
    text = capture.digest(path, path.stat().st_size, max_exchanges=60, max_digest_bytes=80)
    assert len(text.encode()) <= 80
    assert text.startswith(capture.TRUNCATION_MARK + '\n')
    assert text.splitlines()[1:] and all(line.startswith('user: line-') for line in text.splitlines()[1:])
    assert 'line-059' in text
