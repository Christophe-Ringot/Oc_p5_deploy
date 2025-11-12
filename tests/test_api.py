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


def test_predict_one_saves_to_database(client):
    employee_data = {
        "employee_id": 12345,
        "age": 30
    }

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        assert "prediction_id" in data
        prediction_id = data["prediction_id"]

        get_response = client.get(f"/predictions/{prediction_id}")
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["success"] is True
        assert get_data["prediction"]["employee_id"] == 12345


def test_delete_prediction_success(client):
    employee_data = {"age": 28}

    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        prediction_id = post_response.json()["prediction_id"]

        delete_response = client.delete(f"/predictions/{prediction_id}")
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["success"] is True
        assert "supprimée avec succès" in data["message"]

        get_response = client.get(f"/predictions/{prediction_id}")
        assert get_response.status_code == 404


def test_get_prediction_success(client):
    employee_data = {"age": 33}

    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        prediction_id = post_response.json()["prediction_id"]

        get_response = client.get(f"/predictions/{prediction_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["success"] is True
        assert "prediction" in data
        assert "probability" in data["prediction"]
        assert "created_at" in data["prediction"]


def test_predictions_pagination_parameters(client):
    response1 = client.get("/predictions?skip=5&limit=5")
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["skip"] == 5
    assert data1["limit"] == 5

    response2 = client.get("/predictions?skip=0&limit=50")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["skip"] == 0
    assert data2["limit"] == 50


def test_predict_one_with_all_fields(client):
    complete_data = {
        "employee_id": 999,
        "age": 42,
        "nombre_heures_travaillees": 160,
        "annees_experience_totale": 15,
        "annees_dans_l_entreprise": 8,
        "annees_dans_le_poste_actuel": 3,
        "annees_depuis_la_derniere_promotion": 2,
        "revenu_mensuel": 7500.0,
        "heure_supplementaires": 10,
        "ayant_enfants": 2,
        "distance_domicile_travail": 25.5,
        "departement": "Research & Development",
        "niveau_education": 4,
        "domaine_etude": "Medical",
        "genre": "Female",
        "poste": "Research Director",
        "statut_marital": "Divorced",
        "nombre_experiences_precedentes": 5,
        "note_evaluation_precedente": 4,
        "note_evaluation_actuelle": 4,
        "augmentation_salaire_precedente": 0.20,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equilibre_pro_perso": 2,
        "satisfaction_employee_environnement": 3,
        "satisfaction_employee_equipe": 4,
        "implication_employee": 4,
        "annes_sous_responsable_actuel": 3,
        "nombre_employee_sous_responsabilite": 5,
        "niveau_hierarchique_poste": 4,
        "nb_formations_suivies": 6,
        "frequence_deplacement": "Travel_Frequently",
        "nombre_participation_pee": 3
    }

    response = client.post("/predict_one", json=complete_data)
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert data["prediction"]["probability"] >= 0
        assert data["prediction"]["probability"] <= 1


def test_health_endpoint_details(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["model_loaded"], bool)
    assert isinstance(data["database_url_configured"], bool)
    assert data["status"] in ["healthy", "unhealthy"]


def test_root_endpoint_has_all_routes(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()

    expected_endpoints = ["predict", "predict_one", "predictions", "prediction_by_id", "delete_prediction", "health", "docs"]

    for endpoint in expected_endpoints:
        assert endpoint in data["endpoints"]


def test_predict_one_edge_case_values(client):
    edge_case_data = {
        "age": 18,
        "revenu_mensuel": 1000.0,
        "distance_domicile_travail": 0.5,
        "nombre_heures_travaillees": 40
    }

    response = client.post("/predict_one", json=edge_case_data)
    assert response.status_code in [200, 503]


def test_multiple_predictions_different_employees(client):
    employees = [
        {"employee_id": 1001, "age": 25},
        {"employee_id": 1002, "age": 35},
        {"employee_id": 1003, "age": 45}
    ]

    for employee in employees:
        response = client.post("/predict_one", json=employee)
        if response.status_code == 200:
            assert response.json()["success"] is True
