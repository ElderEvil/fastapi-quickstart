"""Tests for configuration and settings."""

import os
from unittest.mock import patch

from src.fastapi_quickstart.core.config import Settings


def test_default_settings():
    """Test default settings values."""
    settings = Settings()

    assert settings.ENVIRONMENT == "development"
    assert settings.DB_TYPE == "sqlite"
    assert settings.DB_NAME == "app.db"
    assert settings.DB_POOL_SIZE == 83
    assert settings.WEB_CONCURRENCY == 9
    assert settings.MAX_OVERFLOW == 64


def test_sqlite_uri_generation():
    """Test SQLite URI generation."""
    with patch.dict(os.environ, {"DB_TYPE": "sqlite", "DB_NAME": "test.db"}, clear=True):
        settings = Settings()
        assert "sqlite+aiosqlite:///test.db" in settings.ASYNC_DATABASE_URI


def test_postgres_uri_generation():
    """Test PostgreSQL URI generation."""
    env_vars = {
        "DB_TYPE": "postgres",
        "DB_USER": "testuser",
        "DB_PASSWORD": "testpass",
        "DB_HOST": "localhost",
        "DB_NAME": "testdb",
    }

    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()
        uri = settings.ASYNC_DATABASE_URI

        assert "postgresql+asyncpg://" in uri
        assert "testuser" in uri
        assert "testpass" in uri
        assert "localhost" in uri
        assert "testdb" in uri


def test_pool_size_calculation():
    """Test dynamic pool size calculation."""
    with patch.dict(os.environ, {"DB_POOL_SIZE": "100", "WEB_CONCURRENCY": "10"}, clear=True):
        settings = Settings()
        assert settings.pool_size == 10  # 100 // 10


def test_pool_size_minimum():
    """Test pool size minimum value."""
    with patch.dict(os.environ, {"DB_POOL_SIZE": "20", "WEB_CONCURRENCY": "10"}, clear=True):
        settings = Settings()
        # 20 // 10 = 2, but minimum is 5
        assert settings.pool_size == 5


def test_explicit_async_database_uri():
    """Test that explicitly set ASYNC_DATABASE_URI is not overridden."""
    custom_uri = "postgresql+asyncpg://custom:pass@customhost/customdb"

    with patch.dict(os.environ, {"ASYNC_DATABASE_URI": custom_uri}, clear=True):
        settings = Settings()
        # If explicitly set, it should be used as-is
        assert custom_uri in settings.ASYNC_DATABASE_URI
