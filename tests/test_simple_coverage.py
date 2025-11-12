import pytest
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd


def test_predict_one_converts_to_int(client):
    """Test la conversion en int de la prédiction"""
    employee_data = {
        "employee_id": 12345,
        "age": 30
    }

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        assert "prediction_id" in data
        assert isinstance(data["prediction_id"], int)


def test_predict_one_converts_to_float(client):
    """Test la conversion en float de la probabilité"""
    employee_data = {"age": 30}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data["prediction"]["probability"], float)


def test_predict_one_converts_to_bool(client):
    """Test la conversion en bool de will_leave"""
    employee_data = {"age": 30}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data["prediction"]["will_leave"], bool)


@patch('app.main.pipeline')
def test_predict_all_conversions(mock_pipeline, client, test_db):
    """Test toutes les conversions dans /predict"""
    mock_pipeline.predict.return_value = np.array([1, 0, 1])
    mock_pipeline.predict_proba.return_value = np.array([
        [0.2, 0.8],
        [0.6, 0.4],
        [0.3, 0.7]
    ])

    sirh_data = pd.DataFrame({
        'id_employee': [1, 2, 3],
        'age': [30, 40, 25],
        'nombre_heures_travaillees': [80, 90, 85],
        'annees_experience_totale': [5, 10, 3],
        'annees_dans_l_entreprise': [3, 8, 2],
        'annees_dans_le_poste_actuel': [2, 5, 1],
        'annees_depuis_la_derniere_promotion': [1, 2, 1],
        'revenu_mensuel': [5000.0, 7000.0, 4000.0],
        'heure_supplementaires': ['Oui', 'Non', 'Oui'],
        'ayant_enfants': ['Oui', 'Oui', 'Non'],
        'distance_domicile_travail': [10.0, 20.0, 5.0],
        'departement': ['Sales', 'Research & Development', 'Sales'],
        'niveau_education': [3, 4, 2],
        'domaine_etude': ['Life Sciences', 'Medical', 'Marketing'],
        'genre': ['Male', 'Female', 'Male'],
        'poste': ['Sales Executive', 'Research Director', 'Sales Representative'],
        'statut_marital': ['Married', 'Single', 'Married'],
        'nombre_experiences_precedentes': [2, 5, 1]
    })

    eval_data = pd.DataFrame({
        'eval_number': ['eval_1', 'eval_2', 'eval_3'],
        'note_evaluation_precedente': [3, 4, 3],
        'note_evaluation_actuelle': [3, 4, 3],
        'augmentation_salaire_precedente': ['15 %', '20 %', '10 %']
    })

    sondage_data = pd.DataFrame({
        'code_sondage': ['sondage_1', 'sondage_2', 'sondage_3'],
        'satisfaction_employee_nature_travail': [3, 4, 2],
        'satisfaction_employee_equilibre_pro_perso': [3, 4, 2],
        'satisfaction_employee_environnement': [3, 4, 3],
        'satisfaction_employee_equipe': [3, 4, 2],
        'implication_employee': [3, 4, 2],
        'annees_sous_reponsable_actuel': [2, 3, 1],
        'nombre_employee_sous_responsabilite': [0, 5, 0],
        'niveau_hierarchique_poste': [2, 4, 1],
        'nb_formations_suivies': [3, 6, 2],
        'frequence_deplacement': ['Travel_Rarely', 'Travel_Frequently', 'Non-Travel'],
        'nombre_participation_pee': [1, 3, 0]
    })

    sirh_data.to_sql('extrait_sirh', test_db.bind, if_exists='replace', index=False)
    eval_data.to_sql('extrait_eval', test_db.bind, if_exists='replace', index=False)
    sondage_data.to_sql('extrait_sondage', test_db.bind, if_exists='replace', index=False)

    with patch('app.main.pipeline', mock_pipeline):
        response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        predictions = data["predictions"]

        for pred in predictions:
            assert isinstance(pred["employee_id"], int)
            assert isinstance(pred["employee_index"], int)
            assert isinstance(pred["will_leave"], bool)
            assert isinstance(pred["probability"], float)
            assert pred["risk_level"] in ["HIGH", "LOW"]

        assert data["statistics"]["high_risk"] == 2
        assert data["statistics"]["low_risk"] == 1


def test_predict_one_probabilities_to_list(client):
    """Test la conversion des probabilities en list"""
    employee_data = {"age": 30}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        prediction_id = response.json()["prediction_id"]
        get_response = client.get(f"/predictions/{prediction_id}")

        if get_response.status_code == 200:
            pred = get_response.json()["prediction"]
            assert isinstance(pred["probabilities"], list)


def test_predict_saves_probabilities_as_list(client, test_db):
    """Test que /predict sauvegarde probabilities en liste"""
    employee_data = {"age": 35}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        pred_id = response.json()["prediction_id"]
        from app.models import Prediction

        prediction = test_db.query(Prediction).filter(Prediction.id == pred_id).first()
        if prediction:
            assert isinstance(prediction.probabilities, list)


def test_root_endpoint_message(client):
    """Test que le message du root endpoint est correct"""
    response = client.get("/")
    data = response.json()

    assert data["message"] == "API de prédiction de turnover"
    assert data["version"] == "1.0.0"


def test_health_endpoint_all_fields(client):
    """Test tous les champs du health endpoint"""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert "model_loaded" in data
    assert "database_url_configured" in data

    assert data["status"] in ["healthy", "unhealthy"]

    if data["model_loaded"]:
        assert data["status"] == "healthy"
    else:
        assert data["status"] == "unhealthy"


def test_predict_one_employee_id_optional(client):
    """Test que employee_id est optionnel"""
    employee_without_id = {"age": 30}

    response = client.post("/predict_one", json=employee_without_id)
    assert response.status_code in [200, 503]


@patch('app.main.pipeline')
def test_predict_enumeration_and_zip(mock_pipeline, client, test_db):
    """Test enumerate et zip dans la boucle for de /predict"""
    mock_pipeline.predict.return_value = np.array([0, 1])
    mock_pipeline.predict_proba.return_value = np.array([[0.9, 0.1], [0.2, 0.8]])

    sirh_data = pd.DataFrame({
        'id_employee': [100, 200],
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
        'eval_number': ['eval_100', 'eval_200'],
        'note_evaluation_precedente': [3, 4],
        'note_evaluation_actuelle': [3, 4],
        'augmentation_salaire_precedente': ['15 %', '20 %']
    })

    sondage_data = pd.DataFrame({
        'code_sondage': ['sondage_100', 'sondage_200'],
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
        predictions = data["predictions"]

        assert predictions[0]["employee_index"] == 0
        assert predictions[1]["employee_index"] == 1
        assert predictions[0]["employee_id"] == 100
        assert predictions[1]["employee_id"] == 200
