"""Tests pour le module database"""
import pytest
from unittest.mock import patch, MagicMock
import os


def test_database_sqlite_configuration():
    """Test la configuration SQLite quand DB_PORT n'est pas défini"""
    with patch.dict(os.environ, {}, clear=True):
        # Recharger le module pour appliquer les changements d'environnement
        import importlib
        import app.database
        importlib.reload(app.database)

        from app.database import DATABASE_URL, engine

        # Vérifier que SQLite est utilisé
        assert "sqlite" in str(engine.url).lower()


def test_database_postgresql_configuration():
    """Test la configuration PostgreSQL quand les variables sont définies"""
    env_vars = {
        'DB_PORT': '5432',
        'POSTGRES_USER': 'testuser',
        'POSTGRES_PASSWORD': 'testpass',
        'DB_HOST': 'localhost',
        'DB_NAME': 'testdb'
    }

    with patch.dict(os.environ, env_vars, clear=True):
        # Recharger le module
        import importlib
        import app.database
        importlib.reload(app.database)

        from app.database import DATABASE_URL, engine

        # Vérifier que PostgreSQL est utilisé
        assert "postgresql" in str(engine.url).lower()


def test_get_db_yields_session():
    """Test que get_db yield une session et la ferme"""
    from app.database import get_db

    # Obtenir le générateur
    db_gen = get_db()

    # Obtenir la session
    db = next(db_gen)

    # Vérifier que c'est une session
    assert db is not None
    assert hasattr(db, 'query')
    assert hasattr(db, 'commit')
    assert hasattr(db, 'close')

    # Fermer le générateur (devrait fermer la session)
    try:
        next(db_gen)
    except StopIteration:
        pass  # C'est attendu


def test_get_db_closes_session_on_exception():
    """Test que get_db ferme la session même en cas d'exception"""
    from app.database import get_db

    db_gen = get_db()

    try:
        db = next(db_gen)
        # Simuler une exception
        raise ValueError("Test exception")
    except ValueError:
        pass
    finally:
        # Vérifier que la session est fermée
        try:
            db_gen.throw(ValueError, "cleanup")
        except (StopIteration, ValueError):
            pass  # C'est attendu


def test_session_local_configuration():
    """Test la configuration de SessionLocal"""
    from app.database import SessionLocal

    assert SessionLocal is not None

    # Créer une session
    session = SessionLocal()
    assert session is not None

    # Vérifier que autoflush est désactivé
    assert session.autoflush is False

    # Vérifier que la session a les méthodes nécessaires
    assert hasattr(session, 'query')
    assert hasattr(session, 'commit')
    assert hasattr(session, 'rollback')

    session.close()


def test_base_declarative():
    """Test que Base est une classe déclarative"""
    from app.database import Base

    assert Base is not None
    assert hasattr(Base, 'metadata')
    assert hasattr(Base.metadata, 'create_all')
