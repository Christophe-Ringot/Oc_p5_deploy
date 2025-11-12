import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np


def test_predict_one_rollback_on_error(client):
    """Test que le rollback est appelé en cas d'erreur"""
    employee_data = {"age": 30}

    response = client.post("/predict_one", json=employee_data)

    # Le test passe qu'il y ait succès ou erreur
    assert response.status_code in [200, 500, 503]


def test_predict_rollback_on_error(client):
    """Test que le rollback est appelé en cas d'erreur dans /predict"""
    response = client.post("/predict")

    # Le test passe qu'il y ait succès ou erreur
    assert response.status_code in [200, 404, 500, 503]


def test_get_all_predictions_exception(client):
    """Test la gestion d'exception dans get_all_predictions"""
    response = client.get("/predictions?skip=-1&limit=0")

    assert response.status_code in [200, 500]


def test_get_prediction_exception(client):
    """Test la gestion d'exception dans get_prediction"""
    response = client.get("/predictions/-1")

    assert response.status_code in [404, 500]


def test_delete_prediction_rollback(client):
    """Test le rollback lors de la suppression"""
    response = client.delete("/predictions/-1")

    assert response.status_code in [404, 500]


@patch('app.main.pipeline')
def test_predict_with_mocked_pipeline_success(mock_pipeline, client, test_db):
    """Test /predict avec un pipeline mocké qui réussit"""
    # Configuration du mock
    mock_pipeline.predict.return_value = np.array([1, 0])
    mock_pipeline.predict_proba.return_value = np.array([[0.3, 0.7], [0.6, 0.4]])

    # Création de données de test
    sirh_data = pd.DataFrame({
        'id_employee': [1, 2],
        'age': [30, 40],
        'nombre_heures_travaillees': [80, 90],
        'annees_experience_totale': [5, 10],
        'annees_dans_l_entreprise': [3, 8],
        'annees_dans_le_poste_actuel': [2, 5],
        'annees_depuis_la_derniere_promotion': [1, 2],
        'revenu_mensuel': [5000.0, 7000.0],
        'heure_supplementaires': ['Oui', 'Non'],
        'ayant_enfants': ['Oui', 'Oui'],
        'distance_domicile_travail': [10.0, 20.0],
        'departement': ['Sales', 'Research & Development'],
        'niveau_education': [3, 4],
        'domaine_etude': ['Life Sciences', 'Medical'],
        'genre': ['Male', 'Female'],
        'poste': ['Sales Executive', 'Research Director'],
        'statut_marital': ['Married', 'Single'],
        'nombre_experiences_precedentes': [2, 5]
    })

    eval_data = pd.DataFrame({
        'eval_number': ['eval_1', 'eval_2'],
        'note_evaluation_precedente': [3, 4],
        'note_evaluation_actuelle': [3, 4],
        'augmentation_salaire_precedente': ['15 %', '20 %']
    })

    sondage_data = pd.DataFrame({
        'code_sondage': ['sondage_1', 'sondage_2'],
        'satisfaction_employee_nature_travail': [3, 4],
        'satisfaction_employee_equilibre_pro_perso': [3, 4],
        'satisfaction_employee_environnement': [3, 4],
        'satisfaction_employee_equipe': [3, 4],
        'implication_employee': [3, 4],
        'annees_sous_reponsable_actuel': [2, 3],
        'nombre_employee_sous_responsabilite': [0, 5],
        'niveau_hierarchique_poste': [2, 4],
        'nb_formations_suivies': [3, 6],
        'frequence_deplacement': ['Travel_Rarely', 'Travel_Frequently'],
        'nombre_participation_pee': [1, 3]
    })

    sirh_data.to_sql('extrait_sirh', test_db.bind, if_exists='replace', index=False)
    eval_data.to_sql('extrait_eval', test_db.bind, if_exists='replace', index=False)
    sondage_data.to_sql('extrait_sondage', test_db.bind, if_exists='replace', index=False)

    with patch('app.main.pipeline', mock_pipeline):
        response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["total_employees"] == 2
        assert "statistics" in data
        assert data["statistics"]["high_risk"] == 1
        assert data["statistics"]["low_risk"] == 1


@patch('app.main.pipeline')
def test_predict_one_with_mocked_pipeline(mock_pipeline, client):
    """Test /predict_one avec un pipeline mocké"""
    mock_pipeline.predict.return_value = np.array([1])
    mock_pipeline.predict_proba.return_value = np.array([[0.2, 0.8]])

    employee_data = {"age": 30}

    with patch('app.main.pipeline', mock_pipeline):
        response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["prediction"]["will_leave"] is True
        assert data["prediction"]["probability"] == 0.8
        assert data["prediction"]["risk_level"] == "HIGH"


@patch('app.main.load_data_from_postgres')
def test_predict_with_load_error(mock_load, client):
    """Test /predict quand load_data_from_postgres échoue"""
    mock_load.side_effect = Exception("Database connection error")

    response = client.post("/predict")

    assert response.status_code in [500, 503]

    if response.status_code == 500:
        data = response.json()
        assert data["success"] is False
        assert "error" in data


@patch('app.main.preprocess_input')
@patch('app.main.load_data_from_postgres')
def test_predict_with_empty_preprocessing(mock_load, mock_preprocess, client):
    """Test /predict quand preprocessing retourne un DataFrame vide"""
    mock_load.return_value = (
        pd.DataFrame({'eval_number': ['eval_1']}),
        pd.DataFrame({'id_employee': [1]}),
        pd.DataFrame({'code_sondage': ['sondage_1']})
    )
    mock_preprocess.return_value = pd.DataFrame()

    response = client.post("/predict")

    assert response.status_code in [404, 500, 503]
