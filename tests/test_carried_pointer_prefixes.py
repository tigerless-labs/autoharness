import pytest

from autoharness.lib import validate

BODY = '---\nname: foo\ndescription: Use when formatting dates.\n---\nUse strftime.\n'
INTENT = {'action': 'create', 'name': 'foo', 'level': 'project', 'reason': 'observed reuse', 'evidence': 'fixture evidence', 'files': {'scripts/run.sh': 'echo fixture\n'}}


@pytest.mark.parametrize('prefix', ['./', '${CLAUDE_SKILL_DIR}/'])
def test_recognized_local_prefix_is_an_exact_carried_pointer(prefix):
    result = validate.validate(INTENT, BODY + f'Run `{prefix}scripts/run.sh`.\n')
    assert result['ok'], result['findings']


@pytest.mark.parametrize('ref', ['unrelated/scripts/run.sh', './scripts/run.sh.bak', '${CLAUDE_SKILL_DIR}/scripts/run.sh.bak'])
def test_unrelated_prefix_or_longer_filename_does_not_reference_carried_file(ref):
    result = validate.validate(INTENT, BODY + f'Run `{ref}`.\n')
    assert any(family == 'structure' and 'not referenced' in detail for family, detail in result['findings'])


@pytest.mark.parametrize('line', ['Run scripts/run.sh.', 'Run scripts/run.sh, then stop.', 'Run ./scripts/run.sh.'])
def test_sentence_punctuation_after_a_bare_pointer_is_not_part_of_the_path(tmp_path, line):
    result = validate.validate(INTENT, BODY + line + '\n', base_dir=tmp_path)
    assert result['ok'], result['findings']
