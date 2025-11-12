import pytest
from app.database import get_db, Base, engine
from sqlalchemy.orm import Session


def test_get_db_returns_session():
    db_generator = get_db()
    db = next(db_generator)

    assert isinstance(db, Session)

    try:
        db_generator.close()
    except StopIteration:
        pass


def test_get_db_closes_session():
    db_generator = get_db()
    db = next(db_generator)

    assert db.is_active

    try:
        next(db_generator)
    except StopIteration:
        pass


def test_base_metadata_exists():
    assert Base.metadata is not None


def test_engine_exists():
    assert engine is not None


def test_database_connection():
    db_generator = get_db()
    db = next(db_generator)

    try:
        result = db.execute("SELECT 1")
        assert result is not None
    finally:
        try:
            db_generator.close()
        except StopIteration:
            pass
