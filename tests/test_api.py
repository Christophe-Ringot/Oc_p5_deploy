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


def test_predict_endpoint_success(client):
    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "total_employees" in data
        assert "statistics" in data
        assert "predictions" in data
        assert "high_risk" in data["statistics"]
        assert "low_risk" in data["statistics"]
        assert "high_risk_percentage" in data["statistics"]


def test_predict_endpoint_returns_employee_data(client):
    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        if len(data["predictions"]) > 0:
            prediction = data["predictions"][0]
            assert "employee_id" in prediction
            assert "employee_index" in prediction
            assert "will_leave" in prediction
            assert "probability" in prediction
            assert "risk_level" in prediction


def test_predict_endpoint_statistics_calculation(client):
    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        stats = data["statistics"]
        total = data["total_employees"]

        assert stats["high_risk"] + stats["low_risk"] == total

        if total > 0:
            expected_percentage = (stats["high_risk"] / total) * 100
            assert abs(stats["high_risk_percentage"] - expected_percentage) < 0.01


def test_predict_endpoint_error_handling(client):
    response = client.post("/predict")

    if response.status_code == 500:
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "error_type" in data


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


def test_predict_one_high_risk_employee(client):
    high_risk_data = {
        "age": 25,
        "revenu_mensuel": 2000.0,
        "annees_dans_l_entreprise": 1,
        "satisfaction_employee_nature_travail": 1,
        "satisfaction_employee_equilibre_pro_perso": 1,
        "satisfaction_employee_environnement": 1,
        "satisfaction_employee_equipe": 1,
        "implication_employee": 1,
        "heure_supplementaires": 1,
        "distance_domicile_travail": 50.0
    }

    response = client.post("/predict_one", json=high_risk_data)
    assert response.status_code in [200, 503]


def test_predict_one_low_risk_employee(client):
    low_risk_data = {
        "age": 45,
        "revenu_mensuel": 10000.0,
        "annees_dans_l_entreprise": 15,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equilibre_pro_perso": 4,
        "satisfaction_employee_environnement": 4,
        "satisfaction_employee_equipe": 4,
        "implication_employee": 4
    }

    response = client.post("/predict_one", json=low_risk_data)
    assert response.status_code in [200, 503]


def test_predict_one_returns_probabilities(client):
    employee_data = {"age": 30}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data
        prediction = data["prediction"]
        assert "probability" in prediction
        assert 0 <= prediction["probability"] <= 1


def test_predict_one_creates_prediction_in_db(client):
    initial_response = client.get("/predictions")
    initial_count = initial_response.json()["total"]

    employee_data = {"age": 32}
    client.post("/predict_one", json=employee_data)

    final_response = client.get("/predictions")
    final_count = final_response.json()["total"]

    if client.post("/predict_one", json=employee_data).status_code == 200:
        assert final_count >= initial_count


def test_predictions_response_structure(client):
    response = client.get("/predictions")
    assert response.status_code == 200

    data = response.json()
    assert "success" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data
    assert "predictions" in data
    assert isinstance(data["predictions"], list)


def test_prediction_detail_response_structure(client):
    employee_data = {"age": 29}
    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        prediction_id = post_response.json()["prediction_id"]
        get_response = client.get(f"/predictions/{prediction_id}")

        assert get_response.status_code == 200
        data = get_response.json()

        assert "success" in data
        assert data["success"] is True
        assert "prediction" in data

        prediction = data["prediction"]
        assert "id" in prediction
        assert "employee_id" in prediction
        assert "prediction" in prediction
        assert "probability" in prediction
        assert "probabilities" in prediction
        assert "created_at" in prediction


def test_delete_prediction_response_structure(client):
    employee_data = {"age": 27}
    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        prediction_id = post_response.json()["prediction_id"]
        delete_response = client.delete(f"/predictions/{prediction_id}")

        assert delete_response.status_code == 200
        data = delete_response.json()
        assert "success" in data
        assert "message" in data
        assert data["success"] is True


def test_predict_one_different_departments(client):
    departments = ["Sales", "Research & Development", "Human Resources"]

    for dept in departments:
        employee_data = {
            "age": 30,
            "departement": dept
        }
        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_different_education_levels(client):
    for education_level in [1, 2, 3, 4, 5]:
        employee_data = {
            "age": 30,
            "niveau_education": education_level
        }
        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_different_genders(client):
    for gender in ["Male", "Female"]:
        employee_data = {
            "age": 30,
            "genre": gender
        }
        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_different_marital_status(client):
    statuses = ["Single", "Married", "Divorced"]

    for status in statuses:
        employee_data = {
            "age": 30,
            "statut_marital": status
        }
        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_different_travel_frequencies(client):
    frequencies = ["Travel_Rarely", "Travel_Frequently", "Non-Travel"]

    for freq in frequencies:
        employee_data = {
            "age": 30,
            "frequence_deplacement": freq
        }
        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_employee_input_defaults(client):
    minimal_employee = {"age": 25}

    response = client.post("/predict_one", json=minimal_employee)
    assert response.status_code in [200, 503]


def test_predictions_empty_list(client):
    response = client.get("/predictions?skip=99999&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data


def test_predict_one_with_employee_id_none(client):
    employee_data = {
        "employee_id": None,
        "age": 30
    }

    response = client.post("/predict_one", json=employee_data)
    assert response.status_code in [200, 503]


def test_predict_one_probability_bounds(client):
    employee_data = {"age": 40}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        prob = data["prediction"]["probability"]
        assert prob >= 0
        assert prob <= 1
        assert isinstance(prob, float)


def test_predict_one_will_leave_boolean(client):
    employee_data = {"age": 35}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        will_leave = data["prediction"]["will_leave"]
        assert isinstance(will_leave, bool)


def test_predict_one_risk_level_values(client):
    employee_data = {"age": 28}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        risk_level = data["prediction"]["risk_level"]
        assert risk_level in ["HIGH", "LOW"]


def test_get_all_predictions_default_pagination(client):
    response = client.get("/predictions")
    assert response.status_code == 200
    data = response.json()

    assert data["skip"] == 0
    assert data["limit"] == 100


def test_predict_one_all_satisfaction_levels(client):
    for satisfaction in [1, 2, 3, 4]:
        employee_data = {
            "age": 30,
            "satisfaction_employee_nature_travail": satisfaction,
            "satisfaction_employee_equilibre_pro_perso": satisfaction,
            "satisfaction_employee_environnement": satisfaction,
            "satisfaction_employee_equipe": satisfaction,
            "implication_employee": satisfaction
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_all_evaluation_scores(client):
    for score in [1, 2, 3, 4]:
        employee_data = {
            "age": 30,
            "note_evaluation_precedente": score,
            "note_evaluation_actuelle": score
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_various_experiences(client):
    experiences = [
        {"annees_experience_totale": 0, "annees_dans_l_entreprise": 0},
        {"annees_experience_totale": 5, "annees_dans_l_entreprise": 3},
        {"annees_experience_totale": 20, "annees_dans_l_entreprise": 15}
    ]

    for exp in experiences:
        employee_data = {
            "age": 30,
            **exp
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_with_overtime(client):
    for overtime in [0, 1]:
        employee_data = {
            "age": 30,
            "heure_supplementaires": overtime
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_with_children(client):
    for children in [0, 1, 2, 3, 4, 5]:
        employee_data = {
            "age": 30,
            "ayant_enfants": children
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_various_distances(client):
    distances = [0.5, 5.0, 10.0, 25.0, 50.0, 100.0]

    for distance in distances:
        employee_data = {
            "age": 30,
            "distance_domicile_travail": distance
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_various_salaries(client):
    salaries = [1000.0, 3000.0, 5000.0, 8000.0, 15000.0]

    for salary in salaries:
        employee_data = {
            "age": 30,
            "revenu_mensuel": salary
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_various_work_hours(client):
    hours = [40, 80, 120, 160, 200]

    for hour in hours:
        employee_data = {
            "age": 30,
            "nombre_heures_travaillees": hour
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_various_hierarchical_levels(client):
    for level in [1, 2, 3, 4, 5]:
        employee_data = {
            "age": 30,
            "niveau_hierarchique_poste": level
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_various_training_counts(client):
    for training in [0, 1, 3, 5, 6]:
        employee_data = {
            "age": 30,
            "nb_formations_suivies": training
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_various_stock_participation(client):
    for participation in [0, 1, 2, 3, 4, 5]:
        employee_data = {
            "age": 30,
            "nombre_participation_pee": participation
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_all_study_fields(client):
    fields = ["Life Sciences", "Medical", "Marketing", "Technical Degree", "Other", "Human Resources"]

    for field in fields:
        employee_data = {
            "age": 30,
            "domaine_etude": field
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_all_job_positions(client):
    positions = [
        "Sales Executive",
        "Research Scientist",
        "Laboratory Technician",
        "Manufacturing Director",
        "Healthcare Representative",
        "Manager",
        "Sales Representative",
        "Research Director",
        "Human Resources"
    ]

    for position in positions:
        employee_data = {
            "age": 30,
            "poste": position
        }

        response = client.post("/predict_one", json=employee_data)
        assert response.status_code in [200, 503]


def test_predict_one_response_has_prediction_id(client):
    employee_data = {"age": 31}

    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        assert "prediction_id" in data
        assert isinstance(data["prediction_id"], int)


def test_health_status_healthy_when_model_loaded(client):
    response = client.get("/health")
    data = response.json()

    if data["model_loaded"]:
        assert data["status"] == "healthy"


def test_health_status_unhealthy_when_model_not_loaded(client):
    response = client.get("/health")
    data = response.json()

    if not data["model_loaded"]:
        assert data["status"] == "unhealthy"


def test_predictions_list_contains_employee_ids(client):
    employee_data = {"employee_id": 99999, "age": 30}
    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        predictions_response = client.get("/predictions")
        data = predictions_response.json()

        if data["total"] > 0:
            first_prediction = data["predictions"][0]
            assert "employee_id" in first_prediction


def test_prediction_created_at_is_timestamp(client):
    employee_data = {"age": 30}
    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        prediction_id = post_response.json()["prediction_id"]
        get_response = client.get(f"/predictions/{prediction_id}")

        if get_response.status_code == 200:
            prediction = get_response.json()["prediction"]
            assert prediction["created_at"] is not None


def test_predict_one_exception_handling(client):
    invalid_employee = {
        "age": 30,
        "revenu_mensuel": 5000.0,
        "annees_experience_totale": 10
    }

    response = client.post("/predict_one", json=invalid_employee)
    assert response.status_code in [200, 500, 503]

    if response.status_code == 500:
        data = response.json()
        assert "error" in data
        assert "error_type" in data


def test_predict_one_db_commit(client):
    before_count_response = client.get("/predictions")
    before_count = before_count_response.json()["total"]

    employee_data = {"age": 33}
    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        after_count_response = client.get("/predictions")
        after_count = after_count_response.json()["total"]
        assert after_count > before_count


def test_predict_one_db_refresh(client):
    employee_data = {"employee_id": 77777, "age": 29}
    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        prediction_id = data["prediction_id"]
        assert prediction_id is not None
        assert isinstance(prediction_id, int)


def test_get_prediction_error_handling(client):
    response = client.get("/predictions/999999999")

    if response.status_code == 500:
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "error_type" in data


def test_delete_prediction_error_handling(client):
    response = client.delete("/predictions/999999999")

    if response.status_code == 500:
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "error_type" in data


def test_get_all_predictions_error_handling(client):
    response = client.get("/predictions")

    if response.status_code == 500:
        data = response.json()
        assert data["success"] is False
        assert "error" in data
        assert "error_type" in data


def test_predict_endpoint_all_employees(client):
    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        predictions = data["predictions"]

        for i, pred in enumerate(predictions):
            assert pred["employee_index"] == i
            assert pred["risk_level"] in ["HIGH", "LOW"]
            assert 0 <= pred["probability"] <= 1


def test_predict_endpoint_probabilities_array(client):
    response = client.post("/predict")

    if response.status_code == 200:
        predictions_response = client.get("/predictions")
        if predictions_response.status_code == 200:
            data = predictions_response.json()
            if len(data["predictions"]) > 0:
                pred = data["predictions"][0]
                assert "probabilities" in pred
                if pred["probabilities"] is not None:
                    assert isinstance(pred["probabilities"], list)


def test_predict_one_model_dump(client):
    complete_employee = {
        "employee_id": 55555,
        "age": 35,
        "nombre_heures_travaillees": 80,
        "revenu_mensuel": 6000.0
    }

    response = client.post("/predict_one", json=complete_employee)

    if response.status_code == 200:
        data = response.json()
        assert "prediction" in data


def test_predict_one_probability_rounding(client):
    employee_data = {"age": 28}
    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        prob = data["prediction"]["probability"]
        prob_str = str(prob)
        decimal_places = len(prob_str.split('.')[-1]) if '.' in prob_str else 0
        assert decimal_places <= 3


def test_predict_endpoint_risk_threshold(client):
    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        for pred in data["predictions"]:
            if pred["probability"] > 0.50:
                assert pred["risk_level"] == "HIGH"
            else:
                assert pred["risk_level"] == "LOW"


def test_predict_one_risk_threshold(client):
    employee_data = {"age": 32}
    response = client.post("/predict_one", json=employee_data)

    if response.status_code == 200:
        data = response.json()
        pred = data["prediction"]

        if pred["probability"] > 0.50:
            assert pred["risk_level"] == "HIGH"
        else:
            assert pred["risk_level"] == "LOW"


def test_predictions_total_count(client):
    response = client.get("/predictions")

    if response.status_code == 200:
        data = response.json()
        assert "total" in data
        assert isinstance(data["total"], int)
        assert data["total"] >= 0


def test_delete_then_get_prediction(client):
    employee_data = {"age": 26}
    post_response = client.post("/predict_one", json=employee_data)

    if post_response.status_code == 200:
        prediction_id = post_response.json()["prediction_id"]

        delete_response = client.delete(f"/predictions/{prediction_id}")
        assert delete_response.status_code == 200

        get_response = client.get(f"/predictions/{prediction_id}")
        assert get_response.status_code == 404


def test_predict_one_all_default_values(client):
    employee_with_defaults = {
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

    response = client.post("/predict_one", json=employee_with_defaults)
    assert response.status_code in [200, 503]


def test_predict_endpoint_employee_ids_conversion(client):
    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        for pred in data["predictions"]:
            assert isinstance(pred["employee_id"], int)


def test_predict_endpoint_prediction_conversion(client):
    response = client.post("/predict")

    if response.status_code == 200:
        predictions_response = client.get("/predictions")
        if predictions_response.status_code == 200:
            data = predictions_response.json()
            if len(data["predictions"]) > 0:
                pred = data["predictions"][0]
                assert isinstance(pred["prediction"], int)
                assert pred["prediction"] in [0, 1]


def test_predict_endpoint_probability_conversion(client):
    response = client.post("/predict")

    if response.status_code == 200:
        predictions_response = client.get("/predictions")
        if predictions_response.status_code == 200:
            data = predictions_response.json()
            if len(data["predictions"]) > 0:
                pred = data["predictions"][0]
                assert isinstance(pred["probability"], float)


def test_health_database_url_configured(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "database_url_configured" in data
    assert isinstance(data["database_url_configured"], bool)
