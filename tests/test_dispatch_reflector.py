"""Verify _is_reflector uses namespace-qualified match."""
from autoharness.hook.dispatch import _is_reflector

def test_canonical_reflector():
    assert _is_reflector({"agent_type": "autoharness:reflector"})

def test_other_namespace_reflector():
    assert _is_reflector({"agent_type": "myplugin:reflector"})

def test_hyphen_reflector_not_matched():
    assert not _is_reflector({"agent_type": "custom-reflector"})

def test_no_prefix_reflector_not_matched():
    assert not _is_reflector({"agent_type": "reflector"})

def test_unrelated_agent_not_matched():
    assert not _is_reflector({"agent_type": "my-agent"})

def test_empty_agent_type():
    assert not _is_reflector({})
