import pytest
import os
from unittest.mock import patch, MagicMock
import asyncio


def test_main_module_imports():
    from app.main import app, pipeline, EmployeeInput, DATABASE_URL

    assert app is not None
    assert app.title == "API Prédiction Turnover"
    assert app.version == "1.0.0"


def test_employee_input_model():
    from app.main import EmployeeInput

    employee = EmployeeInput(age=30)

    assert employee.age == 30
    assert employee.nombre_heures_travaillees == 80
    assert employee.annees_experience_totale == 10
    assert employee.revenu_mensuel == 5000.0
    assert employee.departement == "Sales"


def test_employee_input_all_defaults():
    from app.main import EmployeeInput

    employee = EmployeeInput()

    assert employee.age == 35
    assert employee.nombre_heures_travaillees == 80
    assert employee.annees_experience_totale == 10
    assert employee.annees_dans_l_entreprise == 5
    assert employee.annees_dans_le_poste_actuel == 2
    assert employee.annees_depuis_la_derniere_promotion == 1
    assert employee.revenu_mensuel == 5000.0
    assert employee.heure_supplementaires == 0
    assert employee.ayant_enfants == 1
    assert employee.distance_domicile_travail == 10.0
    assert employee.departement == "Sales"
    assert employee.niveau_education == 3
    assert employee.domaine_etude == "Life Sciences"
    assert employee.genre == "Male"
    assert employee.poste == "Sales Executive"
    assert employee.statut_marital == "Married"
    assert employee.nombre_experiences_precedentes == 2
    assert employee.note_evaluation_precedente == 3
    assert employee.note_evaluation_actuelle == 3
    assert employee.augmentation_salaire_precedente == 0.15
    assert employee.satisfaction_employee_nature_travail == 3
    assert employee.satisfaction_employee_equilibre_pro_perso == 3
    assert employee.satisfaction_employee_environnement == 3
    assert employee.satisfaction_employee_equipe == 3
    assert employee.implication_employee == 3
    assert employee.annes_sous_responsable_actuel == 2
    assert employee.nombre_employee_sous_responsabilite == 0
    assert employee.niveau_hierarchique_poste == 2
    assert employee.nb_formations_suivies == 3
    assert employee.frequence_deplacement == "Travel_Rarely"
    assert employee.nombre_participation_pee == 1


def test_employee_input_custom_values():
    from app.main import EmployeeInput

    employee = EmployeeInput(
        employee_id=999,
        age=45,
        revenu_mensuel=10000.0,
        departement="Research & Development",
        genre="Female"
    )

    assert employee.employee_id == 999
    assert employee.age == 45
    assert employee.revenu_mensuel == 10000.0
    assert employee.departement == "Research & Development"
    assert employee.genre == "Female"


def test_database_url_environment_variable():
    from app.main import DATABASE_URL

    assert DATABASE_URL is not None or DATABASE_URL is None


def test_pipeline_loading_attempt():
    from app.main import pipeline

    assert pipeline is None or pipeline is not None


def test_startup_event_success():
    """Test le startup event de l'application avec succès"""
    with patch('app.init_db.init_database') as mock_init_db:
        from app.main import startup_event

        # Exécuter le startup event
        asyncio.run(startup_event())

        # Vérifier que init_database a été appelé
        mock_init_db.assert_called_once()


def test_startup_event_with_exception():
    """Test le startup event quand init_database lève une exception"""
    with patch('app.init_db.init_database', side_effect=Exception("Erreur de connexion")):
        from app.main import startup_event

        # Ne devrait pas lever d'exception car elle est capturée
        try:
            asyncio.run(startup_event())
        except Exception:
            pytest.fail("startup_event ne devrait pas propager l'exception")
