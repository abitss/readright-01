from readright.persistence import database


def test_postgres_url_is_normalised_to_psycopg3():
    assert database._normalise_database_url("postgres://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"
    assert database._normalise_database_url("postgresql://user:pass@host/db") == "postgresql+psycopg://user:pass@host/db"


def test_sqlite_url_is_not_rewritten():
    assert database._normalise_database_url("sqlite:///./readright.db") == "sqlite:///./readright.db"


def test_local_test_storage_reports_non_persistent():
    health = database.check_storage()
    assert health.ok is True
    assert health.backend == "sqlite"
    assert health.persistent is False
