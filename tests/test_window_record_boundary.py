import json

from autoharness.hook import capture


def test_review_window_preserves_whole_records_and_marker_separator(tmp_path):
    path = tmp_path / 'transcript.jsonl'
    records = [{'type': 'user', 'message': {'content': f'line-{i:03} ' + 'x' * 18}} for i in range(60)]
    path.write_text('\n'.join(json.dumps(r) for r in records))
    before = path.read_bytes()
    text, offset = capture.window(path, max_window_bytes=300)
    assert len(text.encode()) <= 300
    assert text.startswith(capture.TRUNCATION_MARK + '\n')
    retained = [json.loads(line) for line in text.splitlines()[1:]]
    assert retained and retained[-1] == records[-1]
    assert offset == len(before) and path.read_bytes() == before
