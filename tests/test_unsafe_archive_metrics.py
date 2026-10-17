from autoharness.lib import layer, metrics


def test_unsafe_archived_name_does_not_disable_metrics(tmp_path):
    roots = {'project': tmp_path / 'p', 'global': tmp_path / 'g'}
    for name in ['safe-archive', 'My Notes']:
        path = layer.archive_dir('project', roots['project']) / name / 'SKILL.md'
        path.parent.mkdir(parents=True)
        path.write_text('body')
    report = metrics.collect(roots)['project']
    assert report['archived_total'] == 1
    assert report['deaths']['lifecycle'] == 1
    assert (layer.archive_dir('project', roots['project']) / 'My Notes/SKILL.md').read_text() == 'body'
