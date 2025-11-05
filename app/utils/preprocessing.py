import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.base import BaseEstimator, TransformerMixin


class SafeLogTransform(BaseEstimator, TransformerMixin):
    """
    Transformateur personnalisé pour appliquer log(x + 1) de manière sécurisée.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.log1p(X)


def safe_log_transform(x):
    """
    Fonction de transformation logarithmique sécurisée: log(x + 1)
    """
    return np.log1p(x)

def load_data_from_postgres(db_url: str):
    """
    Charge les 3 tables depuis PostgreSQL.

    Args:
        db_url: URL de connexion PostgreSQL (format: postgresql://user:password@host:port/database)

    Returns:
        Tuple de 3 DataFrames (eval_df, sirh_df, sondage_df)
    """
    engine = create_engine(db_url)

    try:
        eval_df = pd.read_sql("SELECT * FROM extrait_eval", engine)
        sirh_df = pd.read_sql("SELECT * FROM extrait_sirh", engine)
        sondage_df = pd.read_sql("SELECT * FROM extrait_sondage", engine)
    finally:
        engine.dispose()

    return eval_df, sirh_df, sondage_df


def preprocess_input(eval_df, sirh_df, sondage_df):
    """
    Applique tout le preprocessing nécessaire avant de passer au pipeline sklearn.

    Args:
        eval_df: DataFrame des évaluations
        sirh_df: DataFrame SIRH
        sondage_df: DataFrame des sondages

    Returns:
        X: DataFrame prêt pour pipeline.predict()
    """

    # ÉTAPE 1: Renommer les colonnes (fix typos)
    sirh_df = sirh_df.rename(columns={
        'nombre_heures_travailless': 'nombre_heures_travaillees',
        'annee_experience_totale': 'annees_experience_totale'
    })

    eval_df = eval_df.rename(columns={
        'augementation_salaire_precedente': 'augmentation_salaire_precedente'
    })

    sondage_df = sondage_df.rename(columns={
        'annes_sous_reponsable_actuel': 'annees_sous_reponsable_actuel'
    })

    # ÉTAPE 2: Créer les ID pour le merge
    eval_df['id_employee'] = eval_df['eval_number'].astype(str).str.extract('(\d+)').astype(int)
    sondage_df['id_employee'] = sondage_df['code_sondage'].astype(str).str.replace('00000', '').astype(int)

    # ÉTAPE 3: Merger les 3 datasets
    full_df = sirh_df.merge(eval_df, on='id_employee', how='inner')\
                     .merge(sondage_df, on='id_employee', how='inner')

    # ÉTAPE 4: Normaliser le pourcentage
    full_df['augmentation_salaire_precedente'] = full_df['augmentation_salaire_precedente'].apply(
        lambda x: float(str(x).replace(' %', '')) / 100 if isinstance(x, str) else x
    )

    # ÉTAPE 5: Convertir les booléens
    bool_columns = ['heure_supplementaires', 'ayant_enfants']
    for col in bool_columns:
        full_df[col] = full_df[col].apply(lambda x: 1 if x in ['Oui', 'Y'] else 0)

    # ÉTAPE 6: Créer les features engineered
    full_df['experience_ratio'] = full_df['annees_experience_totale'] / (full_df['age'] + 1)
    full_df['age_squared'] = full_df['age'] ** 2
    full_df['satisfaction_equilibre'] = (
        full_df['satisfaction_employee_nature_travail'] *
        full_df['satisfaction_employee_equilibre_pro_perso']
    )
    full_df['experience_ratio_squared'] = full_df['experience_ratio'] ** 2
    full_df['mobilite_ratio'] = (
        full_df['annees_dans_le_poste_actuel'] /
        (full_df['annees_dans_l_entreprise'] + 1)
    )
    full_df['revenu_par_experience'] = (
        full_df['revenu_mensuel'] /
        (full_df['annees_experience_totale'] + 1)
    )

    # ÉTAPE 7: Supprimer les colonnes ID et target (si présente)
    colonnes_a_supprimer = ['eval_number', 'code_sondage']
    if 'a_quitte_l_entreprise' in full_df.columns:
        colonnes_a_supprimer.append('a_quitte_l_entreprise')

    X = full_df.drop(columns=colonnes_a_supprimer)

    return X


def preprocess_single_employee(employee_dict):
    """
    Applique le preprocessing pour un seul employé (sans merge de tables).

    Args:
        employee_dict: Dictionnaire avec les données de l'employé

    Returns:
        DataFrame prêt pour pipeline.predict()
    """
    import pandas as pd

    # Créer un DataFrame
    df = pd.DataFrame([employee_dict])

    # Créer les features engineered
    df['experience_ratio'] = df['annees_experience_totale'] / (df['age'] + 1)
    df['age_squared'] = df['age'] ** 2
    df['satisfaction_equilibre'] = (
        df['satisfaction_employee_nature_travail'] *
        df['satisfaction_employee_equilibre_pro_perso']
    )
    df['experience_ratio_squared'] = df['experience_ratio'] ** 2
    df['mobilite_ratio'] = (
        df['annees_dans_le_poste_actuel'] /
        (df['annees_dans_l_entreprise'] + 1)
    )
    df['revenu_par_experience'] = (
        df['revenu_mensuel'] /
        (df['annees_experience_totale'] + 1)
    )

    return df
