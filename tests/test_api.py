import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "API de prédiction de turnover"
    assert data["version"] == "1.0.0"
    assert "endpoints" in data


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "database_url_configured" in data


def test_predict_one_with_default_values(client):
    employee_data = {
        "employee_id": 1,
        "age": 35,
        "nombre_heures_travaillees": 80,
        "annees_experience_totale": 10,
        "annees_dans_l_entreprise": 5,
        "annees_dans_le_poste_actuel": 2,
        "annees_depuis_la_derniere_promotion": 1,
        "revenu_mensuel": 5000.0,
        "heure_supplementaires": 0,
        "ayant_enfants": 1,
        "distance_domicile_travail": 10.0,
        "departement": "Sales",
        "niveau_education": 3,
        "domaine_etude": "Life Sciences",
        "genre": "Male",
        "poste": "Sales Executive",
        "statut_marital": "Married",
        "nombre_experiences_precedentes": 2,
        "note_evaluation_precedente": 3,
        "note_evaluation_actuelle": 3,
        "augmentation_salaire_precedente": 0.15,
        "satisfaction_employee_nature_travail": 3,
        "satisfaction_employee_equilibre_pro_perso": 3,
        "satisfaction_employee_environnement": 3,
        "satisfaction_employee_equipe": 3,
        "implication_employee": 3,
        "annes_sous_responsable_actuel": 2,
        "nombre_employee_sous_responsabilite": 0,
        "niveau_hierarchique_poste": 2,
        "nb_formations_suivies": 3,
        "frequence_deplacement": "Travel_Rarely",
        "nombre_participation_pee": 1
    }

    response = client.post("/predict_one", json=employee_data)

    assert response.status_code in [200, 503]
    data = response.json()

    if response.status_code == 200:
        assert data["success"] is True
        assert "prediction" in data
        assert "will_leave" in data["prediction"]
        assert "probability" in data["prediction"]
        assert "risk_level" in data["prediction"]
    else:
        assert data["success"] is False
        assert "error" in data


def test_predict_one_invalid_data(client):
    invalid_data = {
        "age": "invalid", 
    }

    response = client.post("/predict_one", json=invalid_data)
    assert response.status_code == 422 


def test_get_all_predictions(client):
    response = client.get("/predictions")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "total" in data
    assert "predictions" in data


def test_get_all_predictions_with_pagination(client):
    response = client.get("/predictions?skip=0&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["skip"] == 0
    assert data["limit"] == 10


def test_get_prediction_not_found(client):
    response = client.get("/predictions/999999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data


def test_delete_prediction_not_found(client):
    response = client.delete("/predictions/999999")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data


def test_predict_endpoint_without_model(client):
    response = client.post("/predict")
    assert response.status_code in [500, 503]
    data = response.json()
    assert data["success"] is False
    assert "error" in data


def test_predict_one_minimal_data(client):
    minimal_data = {
        "age": 30
    }

    response = client.post("/predict_one", json=minimal_data)
    assert response.status_code in [200, 503]
    data = response.json()

    if response.status_code == 200:
        assert data["success"] is True
        assert "prediction" in data
    else:
        assert "error" in data


def test_endpoints_return_json(client):
    endpoints = [
        ("/", "get"),
        ("/health", "get"),
        ("/predictions", "get"),
    ]

    for path, method in endpoints:
        if method == "get":
            response = client.get(path)

        assert response.status_code in [200, 404, 500, 503]
        assert response.headers["content-type"] == "application/json"


def test_risk_level_calculation(client):
    employee_data = {"age": 25}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        prediction = data["prediction"]
        probability = prediction["probability"]
        risk_level = prediction["risk_level"]

        if probability > 0.50:
            assert risk_level == "HIGH"
        else:
            assert risk_level == "LOW"
