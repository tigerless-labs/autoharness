"""Verify _rules lru_cache key is normalized so None and the default path share one entry."""
from autoharness import config
from autoharness.lib import redact

def test_cache_key_normalized():
    redact._rules.cache_clear()
    redact.redact("hello")
    after_none = redact._rules.cache_info()
    redact.redact("hello", rules_path=str(config.REDACTION_RULES))
    after_explicit = redact._rules.cache_info()
    assert after_explicit.hits == after_none.hits + 1, (
        f"expected cache hit on second call, got misses={after_explicit.misses} hits={after_explicit.hits}"
    )
