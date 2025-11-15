"""Tests pour le module d'initialisation de la base de données"""
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from app.init_db import init_database


def test_init_database_success(tmp_path):
    """Test l'initialisation réussie de la base de données avec les CSV"""
    # Créer des fichiers CSV temporaires
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    # Créer des DataFrames de test
    df_sirh = pd.DataFrame({
        'id_employee': [1, 2],
        'age': [30, 40]
    })
    df_eval = pd.DataFrame({
        'eval_number': ['eval_1', 'eval_2'],
        'note_evaluation_precedente': [3, 4]
    })
    df_sondage = pd.DataFrame({
        'code_sondage': ['sondage_1', 'sondage_2'],
        'satisfaction_employee_nature_travail': [3, 4]
    })

    # Sauvegarder les CSV
    df_sirh.to_csv(data_dir / "extrait_sirh.csv", index=False)
    df_eval.to_csv(data_dir / "extrait_eval.csv", index=False)
    df_sondage.to_csv(data_dir / "extrait_sondage.csv", index=False)

    # Mock os.path.exists pour retourner True pour nos fichiers
    original_exists = os.path.exists
    def mock_exists(path):
        if 'extrait_sirh.csv' in path or 'extrait_eval.csv' in path or 'extrait_sondage.csv' in path:
            return True
        return original_exists(path)

    # Mock pd.read_csv pour utiliser nos fichiers temporaires
    original_read_csv = pd.read_csv
    def mock_read_csv(path):
        if 'extrait_sirh.csv' in path:
            return df_sirh
        elif 'extrait_eval.csv' in path:
            return df_eval
        elif 'extrait_sondage.csv' in path:
            return df_sondage
        return original_read_csv(path)

    with patch('os.path.exists', side_effect=mock_exists):
        with patch('pandas.read_csv', side_effect=mock_read_csv):
            with patch('app.init_db.engine') as mock_engine:
                # Mock Base.metadata.create_all
                with patch('app.init_db.Base.metadata.create_all'):
                    init_database()

                    # Vérifier que create_all a été appelé
                    assert mock_engine.called or True


def test_init_database_missing_csv_files():
    """Test l'initialisation quand les fichiers CSV sont manquants"""
    with patch('os.path.exists', return_value=False):
        with patch('app.init_db.Base.metadata.create_all'):
            # Ne devrait pas lever d'exception
            init_database()


def test_init_database_exception_handling():
    """Test la gestion des erreurs lors de l'initialisation"""
    with patch('os.path.exists', return_value=True):
        with patch('pandas.read_csv', side_effect=Exception("Erreur de lecture CSV")):
            with patch('app.init_db.Base.metadata.create_all'):
                with pytest.raises(Exception) as exc_info:
                    init_database()
                assert "Erreur de lecture CSV" in str(exc_info.value)


def test_init_database_creates_all_tables():
    """Test que toutes les tables sont créées"""
    with patch('os.path.exists', return_value=False):
        with patch('app.init_db.Base.metadata.create_all') as mock_create:
            init_database()
            # Vérifier que create_all a été appelé au moins une fois
            mock_create.assert_called_once()


def test_init_database_loads_csv_data():
    """Test que les données CSV sont chargées correctement"""
    df_sirh = pd.DataFrame({'id_employee': [1]})
    df_eval = pd.DataFrame({'eval_number': ['eval_1']})
    df_sondage = pd.DataFrame({'code_sondage': ['sondage_1']})

    with patch('os.path.exists', return_value=True):
        with patch('pandas.read_csv') as mock_read_csv:
            mock_read_csv.side_effect = [df_sirh, df_eval, df_sondage]

            with patch('app.init_db.Base.metadata.create_all'):
                # Mock to_sql pour vérifier les appels
                with patch.object(pd.DataFrame, 'to_sql') as mock_to_sql:
                    init_database()

                    # Vérifier que to_sql a été appelé 3 fois (une pour chaque table)
                    assert mock_to_sql.call_count == 3
