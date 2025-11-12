import pytest
import pandas as pd
import numpy as np
from app.utils.preprocessing import (
    safe_log_transform,
    SafeLogTransform,
    preprocess_single_employee,
    preprocess_input
)


def test_safe_log_transform():
    result = safe_log_transform(10)
    expected = np.log1p(10)
    assert result == expected


def test_safe_log_transform_zero():
    result = safe_log_transform(0)
    assert result == 0


def test_safe_log_transform_array():
    arr = np.array([0, 1, 10, 100])
    result = safe_log_transform(arr)
    expected = np.log1p(arr)
    np.testing.assert_array_equal(result, expected)


def test_SafeLogTransform_fit():
    transformer = SafeLogTransform()
    X = np.array([[1, 2], [3, 4]])
    result = transformer.fit(X)
    assert result is transformer


def test_SafeLogTransform_transform():
    transformer = SafeLogTransform()
    X = np.array([[1, 2], [3, 4]])
    result = transformer.transform(X)
    expected = np.log1p(X)
    np.testing.assert_array_equal(result, expected)


def test_SafeLogTransform_fit_transform():
    transformer = SafeLogTransform()
    X = np.array([[0, 1], [10, 100]])
    result = transformer.fit(X).transform(X)
    expected = np.log1p(X)
    np.testing.assert_array_equal(result, expected)


def test_preprocess_single_employee():
    employee = {
        "age": 30,
        "annees_experience_totale": 5,
        "annees_dans_le_poste_actuel": 2,
        "annees_dans_l_entreprise": 3,
        "revenu_mensuel": 5000,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equilibre_pro_perso": 3
    }

    result = preprocess_single_employee(employee)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 1
    assert "experience_ratio" in result.columns
    assert "age_squared" in result.columns
    assert "satisfaction_equilibre" in result.columns
    assert "experience_ratio_squared" in result.columns
    assert "mobilite_ratio" in result.columns
    assert "revenu_par_experience" in result.columns


def test_preprocess_single_employee_calculated_features():
    employee = {
        "age": 30,
        "annees_experience_totale": 10,
        "annees_dans_le_poste_actuel": 2,
        "annees_dans_l_entreprise": 5,
        "revenu_mensuel": 6000,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equilibre_pro_perso": 3
    }

    result = preprocess_single_employee(employee)

    assert result["age_squared"].values[0] == 900
    assert result["satisfaction_equilibre"].values[0] == 12
    assert result["experience_ratio"].values[0] == pytest.approx(10 / 31)
    assert result["mobilite_ratio"].values[0] == pytest.approx(2 / 6)
    assert result["revenu_par_experience"].values[0] == pytest.approx(6000 / 11)


def test_preprocess_input_empty_dataframes():
    empty_df = pd.DataFrame()
    result = preprocess_input(empty_df, empty_df, empty_df)
    assert result.empty


def test_preprocess_input_with_data():
    sirh_df = pd.DataFrame({
        'id_employee': [1, 2],
        'age': [30, 40],
        'nombre_heures_travaillees': [80, 90],
        'annees_experience_totale': [5, 10],
        'annees_dans_l_entreprise': [3, 8],
        'annees_dans_le_poste_actuel': [2, 5],
        'revenu_mensuel': [5000, 7000],
        'heure_supplementaires': ['Oui', 'Non'],
        'ayant_enfants': ['Oui', 'Non']
    })

    eval_df = pd.DataFrame({
        'eval_number': ['eval_1', 'eval_2'],
        'augmentation_salaire_precedente': ['15 %', '20 %'],
        'note_evaluation_actuelle': [3, 4]
    })

    sondage_df = pd.DataFrame({
        'code_sondage': ['sondage_1', 'sondage_2'],
        'satisfaction_employee_nature_travail': [3, 4],
        'satisfaction_employee_equilibre_pro_perso': [3, 4]
    })

    result = preprocess_input(eval_df, sirh_df, sondage_df)

    assert not result.empty
    assert len(result) == 2
    assert "experience_ratio" in result.columns
    assert "age_squared" in result.columns
    assert "satisfaction_equilibre" in result.columns


def test_preprocess_input_boolean_conversion():
    sirh_df = pd.DataFrame({
        'id_employee': [1],
        'age': [30],
        'nombre_heures_travaillees': [80],
        'annees_experience_totale': [5],
        'annees_dans_l_entreprise': [3],
        'annees_dans_le_poste_actuel': [2],
        'revenu_mensuel': [5000],
        'heure_supplementaires': ['Oui'],
        'ayant_enfants': ['Non']
    })

    eval_df = pd.DataFrame({
        'eval_number': ['eval_1'],
        'augmentation_salaire_precedente': ['15 %']
    })

    sondage_df = pd.DataFrame({
        'code_sondage': ['sondage_1'],
        'satisfaction_employee_nature_travail': [3],
        'satisfaction_employee_equilibre_pro_perso': [3]
    })

    result = preprocess_input(eval_df, sirh_df, sondage_df)

    assert result['heure_supplementaires'].values[0] == 1
    assert result['ayant_enfants'].values[0] == 0


def test_preprocess_input_percentage_conversion():
    sirh_df = pd.DataFrame({
        'id_employee': [1],
        'age': [30],
        'nombre_heures_travaillees': [80],
        'annees_experience_totale': [5],
        'annees_dans_l_entreprise': [3],
        'annees_dans_le_poste_actuel': [2],
        'revenu_mensuel': [5000],
        'heure_supplementaires': ['Oui'],
        'ayant_enfants': ['Oui']
    })

    eval_df = pd.DataFrame({
        'eval_number': ['eval_1'],
        'augmentation_salaire_precedente': ['15 %']
    })

    sondage_df = pd.DataFrame({
        'code_sondage': ['sondage_1'],
        'satisfaction_employee_nature_travail': [3],
        'satisfaction_employee_equilibre_pro_perso': [3]
    })

    result = preprocess_input(eval_df, sirh_df, sondage_df)

    assert result['augmentation_salaire_precedente'].values[0] == pytest.approx(0.15)


def test_preprocess_input_drops_unnecessary_columns():
    sirh_df = pd.DataFrame({
        'id_employee': [1],
        'age': [30],
        'nombre_heures_travaillees': [80],
        'annees_experience_totale': [5],
        'annees_dans_l_entreprise': [3],
        'annees_dans_le_poste_actuel': [2],
        'revenu_mensuel': [5000],
        'heure_supplementaires': ['Oui'],
        'ayant_enfants': ['Oui']
    })

    eval_df = pd.DataFrame({
        'eval_number': ['eval_1'],
        'augmentation_salaire_precedente': ['15 %']
    })

    sondage_df = pd.DataFrame({
        'code_sondage': ['sondage_1'],
        'satisfaction_employee_nature_travail': [3],
        'satisfaction_employee_equilibre_pro_perso': [3]
    })

    result = preprocess_input(eval_df, sirh_df, sondage_df)

    assert 'eval_number' not in result.columns
    assert 'code_sondage' not in result.columns
