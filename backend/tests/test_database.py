"""Guard: the suite must honor the configured database engine."""

import pytest
from django.conf import settings
from django.db import connection


@pytest.mark.django_db
def test_uses_postgres_when_db_url_configured() -> None:
    if not settings.DATABASE_URL.startswith("postgres"):
        pytest.skip("No PostgreSQL URL configured; using SQLite fallback")
    assert connection.vendor == "postgresql"
