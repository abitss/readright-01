from __future__ import annotations

import os
from dataclasses import dataclass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def _normalise_database_url(value: str) -> str:
    """Use psycopg v3 explicitly for Render-style PostgreSQL URLs."""
    if value.startswith("postgres://"):
        value = "postgresql://" + value[len("postgres://"):]
    if value.startswith("postgresql://"):
        value = "postgresql+psycopg://" + value[len("postgresql://"):]
    return value


RAW_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./readright.db")
DATABASE_URL = _normalise_database_url(RAW_DATABASE_URL)
REQUIRE_PERSISTENT_DB = os.getenv("READRIGHT_REQUIRE_PERSISTENT_DB", "0") == "1"


def storage_backend() -> str:
    if DATABASE_URL.startswith("postgresql+"):
        return "postgresql"
    if DATABASE_URL.startswith("sqlite"):
        return "sqlite"
    return "other"


def is_persistent_backend() -> bool:
    return storage_backend() == "postgresql"


if REQUIRE_PERSISTENT_DB and not is_persistent_backend():
    raise RuntimeError(
        "READRIGHT_REQUIRE_PERSISTENT_DB=1 but DATABASE_URL does not point to PostgreSQL. "
        "Refusing to start because learner history would not be durably persisted."
    )

connect_args = {"check_same_thread": False} if storage_backend() == "sqlite" else {}
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300 if storage_backend() == "postgresql" else -1,
    connect_args=connect_args,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


@dataclass(frozen=True)
class StorageHealth:
    ok: bool
    backend: str
    persistent: bool
    requirement_enabled: bool
    error: str | None = None


def check_storage(target: Engine | None = None) -> StorageHealth:
    db_engine = target or engine
    try:
        with db_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return StorageHealth(
            ok=True,
            backend=storage_backend(),
            persistent=is_persistent_backend(),
            requirement_enabled=REQUIRE_PERSISTENT_DB,
        )
    except Exception as exc:  # pragma: no cover - exact DB driver failures vary
        return StorageHealth(
            ok=False,
            backend=storage_backend(),
            persistent=is_persistent_backend(),
            requirement_enabled=REQUIRE_PERSISTENT_DB,
            error=exc.__class__.__name__,
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
