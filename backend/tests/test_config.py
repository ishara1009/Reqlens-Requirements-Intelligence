from app.core.config import Settings


def test_memory_database_fallback_is_development_only():
    assert Settings(environment="development", allow_in_memory_db=True).can_use_in_memory_db is True
    assert Settings(environment="production", allow_in_memory_db=True).can_use_in_memory_db is False

