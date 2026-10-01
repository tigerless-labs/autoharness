"""Verify _int_env warns on invalid values and _bool_env restricts to 0/1."""
import os
import warnings
from unittest.mock import patch

def test_int_env_warns_on_invalid():
    # Reload to pick up patched env
    from autoharness import config as cfg
    with patch.dict(os.environ, {"AUTOHARNESS_TEST_INT": "abc"}):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = cfg._int_env("AUTOHARNESS_TEST_INT", 42)
            assert result == 42
            assert len(w) == 1
            assert "not a valid integer" in str(w[0].message)

def test_int_env_silent_on_missing():
    from autoharness import config as cfg
    with patch.dict(os.environ, {}, clear=True):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = cfg._int_env("AUTOHARNESS_NONEXISTENT_XYZ", 99)
            assert result == 99
            assert len(w) == 0

def test_bool_env_warns_on_non_binary():
    from autoharness import config as cfg
    with patch.dict(os.environ, {"AUTOHARNESS_TEST_BOOL": "2"}):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = cfg._bool_env("AUTOHARNESS_TEST_BOOL", False)
            assert result is True
            assert len(w) == 1
            assert "should be 0 or 1" in str(w[0].message)

def test_bool_env_accepts_0_and_1():
    from autoharness import config as cfg
    with patch.dict(os.environ, {"AUTOHARNESS_TEST_B1": "1", "AUTOHARNESS_TEST_B0": "0"}):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            assert cfg._bool_env("AUTOHARNESS_TEST_B1", False) is True
            assert cfg._bool_env("AUTOHARNESS_TEST_B0", True) is False
            assert len(w) == 0
