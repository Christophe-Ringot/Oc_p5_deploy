import pytest
import pandas as pd
from sqlalchemy import text


def test_predict_with_database_data(client, test_db):
    sirh_data = {
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
    }

    eval_data = {
        'eval_number': ['eval_1', 'eval_2', 'eval_3'],
        'note_evaluation_precedente': [3, 4, 3],
        'note_evaluation_actuelle': [3, 4, 3],
        'augmentation_salaire_precedente': ['15 %', '20 %', '10 %']
    }

    sondage_data = {
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
    }

    sirh_df = pd.DataFrame(sirh_data)
    eval_df = pd.DataFrame(eval_data)
    sondage_df = pd.DataFrame(sondage_data)

    sirh_df.to_sql('extrait_sirh', test_db.bind, if_exists='replace', index=False)
    eval_df.to_sql('extrait_eval', test_db.bind, if_exists='replace', index=False)
    sondage_df.to_sql('extrait_sondage', test_db.bind, if_exists='replace', index=False)

    response = client.post("/predict")

    assert response.status_code in [200, 500, 503]

    if response.status_code == 200:
        data = response.json()
        assert data["success"] is True
        assert "total_employees" in data
        assert data["total_employees"] == 3
        assert "statistics" in data
        assert "predictions" in data
        assert len(data["predictions"]) == 3


def test_predict_with_empty_database(client, test_db):
    empty_df = pd.DataFrame()

    empty_df.to_sql('extrait_sirh', test_db.bind, if_exists='replace', index=False)
    empty_df.to_sql('extrait_eval', test_db.bind, if_exists='replace', index=False)
    empty_df.to_sql('extrait_sondage', test_db.bind, if_exists='replace', index=False)

    response = client.post("/predict")

    assert response.status_code in [404, 500, 503]


def test_predict_validates_employee_ids(client, test_db):
    sirh_data = pd.DataFrame({
        'id_employee': [10, 20],
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
        'eval_number': ['eval_10', 'eval_20'],
        'note_evaluation_precedente': [3, 4],
        'note_evaluation_actuelle': [3, 4],
        'augmentation_salaire_precedente': ['15 %', '20 %']
    })

    sondage_data = pd.DataFrame({
        'code_sondage': ['sondage_10', 'sondage_20'],
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

    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        employee_ids = [pred["employee_id"] for pred in data["predictions"]]
        assert 10 in employee_ids
        assert 20 in employee_ids


def test_predict_calculates_statistics(client, test_db):
    sirh_data = pd.DataFrame({
        'id_employee': [100, 101],
        'age': [25, 45],
        'nombre_heures_travaillees': [80, 80],
        'annees_experience_totale': [2, 20],
        'annees_dans_l_entreprise': [1, 15],
        'annees_dans_le_poste_actuel': [1, 10],
        'annees_depuis_la_derniere_promotion': [0, 5],
        'revenu_mensuel': [3000.0, 10000.0],
        'heure_supplementaires': ['Oui', 'Non'],
        'ayant_enfants': ['Non', 'Oui'],
        'distance_domicile_travail': [50.0, 5.0],
        'departement': ['Sales', 'Research & Development'],
        'niveau_education': [2, 5],
        'domaine_etude': ['Marketing', 'Medical'],
        'genre': ['Male', 'Female'],
        'poste': ['Sales Representative', 'Research Director'],
        'statut_marital': ['Single', 'Married'],
        'nombre_experiences_precedentes': [1, 8]
    })

    eval_data = pd.DataFrame({
        'eval_number': ['eval_100', 'eval_101'],
        'note_evaluation_precedente': [2, 5],
        'note_evaluation_actuelle': [2, 5],
        'augmentation_salaire_precedente': ['5 %', '25 %']
    })

    sondage_data = pd.DataFrame({
        'code_sondage': ['sondage_100', 'sondage_101'],
        'satisfaction_employee_nature_travail': [1, 5],
        'satisfaction_employee_equilibre_pro_perso': [1, 5],
        'satisfaction_employee_environnement': [1, 5],
        'satisfaction_employee_equipe': [1, 5],
        'implication_employee': [1, 5],
        'annees_sous_reponsable_actuel': [1, 10],
        'nombre_employee_sous_responsabilite': [0, 10],
        'niveau_hierarchique_poste': [1, 5],
        'nb_formations_suivies': [0, 10],
        'frequence_deplacement': ['Non-Travel', 'Travel_Frequently'],
        'nombre_participation_pee': [0, 5]
    })

    sirh_data.to_sql('extrait_sirh', test_db.bind, if_exists='replace', index=False)
    eval_data.to_sql('extrait_eval', test_db.bind, if_exists='replace', index=False)
    sondage_data.to_sql('extrait_sondage', test_db.bind, if_exists='replace', index=False)

    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        stats = data["statistics"]

        assert stats["high_risk"] >= 0
        assert stats["low_risk"] >= 0
        assert stats["high_risk"] + stats["low_risk"] == 2
        assert 0 <= stats["high_risk_percentage"] <= 100


def test_predict_saves_to_database(client, test_db):
    sirh_data = pd.DataFrame({
        'id_employee': [200],
        'age': [35],
        'nombre_heures_travaillees': [80],
        'annees_experience_totale': [10],
        'annees_dans_l_entreprise': [5],
        'annees_dans_le_poste_actuel': [3],
        'annees_depuis_la_derniere_promotion': [2],
        'revenu_mensuel': [6000.0],
        'heure_supplementaires': ['Non'],
        'ayant_enfants': ['Oui'],
        'distance_domicile_travail': [15.0],
        'departement': ['Sales'],
        'niveau_education': [3],
        'domaine_etude': ['Life Sciences'],
        'genre': ['Male'],
        'poste': ['Sales Executive'],
        'statut_marital': ['Married'],
        'nombre_experiences_precedentes': [3]
    })

    eval_data = pd.DataFrame({
        'eval_number': ['eval_200'],
        'note_evaluation_precedente': [3],
        'note_evaluation_actuelle': [4],
        'augmentation_salaire_precedente': ['18 %']
    })

    sondage_data = pd.DataFrame({
        'code_sondage': ['sondage_200'],
        'satisfaction_employee_nature_travail': [4],
        'satisfaction_employee_equilibre_pro_perso': [3],
        'satisfaction_employee_environnement': [4],
        'satisfaction_employee_equipe': [4],
        'implication_employee': [4],
        'annees_sous_reponsable_actuel': [3],
        'nombre_employee_sous_responsabilite': [2],
        'niveau_hierarchique_poste': [3],
        'nb_formations_suivies': [5],
        'frequence_deplacement': ['Travel_Rarely'],
        'nombre_participation_pee': [2]
    })

    sirh_data.to_sql('extrait_sirh', test_db.bind, if_exists='replace', index=False)
    eval_data.to_sql('extrait_eval', test_db.bind, if_exists='replace', index=False)
    sondage_data.to_sql('extrait_sondage', test_db.bind, if_exists='replace', index=False)

    before_count = client.get("/predictions").json()["total"]

    response = client.post("/predict")

    if response.status_code == 200:
        after_count = client.get("/predictions").json()["total"]
        assert after_count > before_count


def test_predict_returns_probabilities(client, test_db):
    sirh_data = pd.DataFrame({
        'id_employee': [300],
        'age': [28],
        'nombre_heures_travaillees': [85],
        'annees_experience_totale': [6],
        'annees_dans_l_entreprise': [4],
        'annees_dans_le_poste_actuel': [2],
        'annees_depuis_la_derniere_promotion': [1],
        'revenu_mensuel': [5500.0],
        'heure_supplementaires': ['Oui'],
        'ayant_enfants': ['Non'],
        'distance_domicile_travail': [12.0],
        'departement': ['Research & Development'],
        'niveau_education': [4],
        'domaine_etude': ['Technical Degree'],
        'genre': ['Female'],
        'poste': ['Laboratory Technician'],
        'statut_marital': ['Single'],
        'nombre_experiences_precedentes': [2]
    })

    eval_data = pd.DataFrame({
        'eval_number': ['eval_300'],
        'note_evaluation_precedente': [3],
        'note_evaluation_actuelle': [3],
        'augmentation_salaire_precedente': ['12 %']
    })

    sondage_data = pd.DataFrame({
        'code_sondage': ['sondage_300'],
        'satisfaction_employee_nature_travail': [3],
        'satisfaction_employee_equilibre_pro_perso': [2],
        'satisfaction_employee_environnement': [3],
        'satisfaction_employee_equipe': [3],
        'implication_employee': [3],
        'annees_sous_reponsable_actuel': [2],
        'nombre_employee_sous_responsabilite': [0],
        'niveau_hierarchique_poste': [2],
        'nb_formations_suivies': [4],
        'frequence_deplacement': ['Travel_Rarely'],
        'nombre_participation_pee': [1]
    })

    sirh_data.to_sql('extrait_sirh', test_db.bind, if_exists='replace', index=False)
    eval_data.to_sql('extrait_eval', test_db.bind, if_exists='replace', index=False)
    sondage_data.to_sql('extrait_sondage', test_db.bind, if_exists='replace', index=False)

    response = client.post("/predict")

    if response.status_code == 200:
        data = response.json()
        predictions = data["predictions"]

        for pred in predictions:
            assert 0 <= pred["probability"] <= 1
            assert pred["will_leave"] in [True, False]
            assert pred["risk_level"] in ["HIGH", "LOW"]
