from autoharness.hook import on_session_start, spawn
from autoharness.lib import sidecar, skill_store


def test_unsafe_handwritten_name_does_not_disable_managed_recall(tmp_path):
    roots = {'project': tmp_path / 'p', 'global': tmp_path / 'g'}
    skill_store.write_body('project', 'healthy', '---\nname: healthy\ndescription: useful-healthy\n---\nbody', roots['project'])
    sidecar.create('project', 'healthy', 0, roots['project'])
    handwritten = roots['project'] / 'skills/My Notes/SKILL.md'
    handwritten.parent.mkdir(parents=True)
    handwritten.write_text('---\nname: My Notes\ndescription: handwritten\n---\nbody')
    before = handwritten.read_bytes()
    assert 'useful-healthy' in on_session_start.on_session_start(roots=roots)['context']
    index = spawn.description_index(roots, agent_only=True)
    assert 'useful-healthy' in index and 'handwritten' not in index
    assert handwritten.read_bytes() == before
