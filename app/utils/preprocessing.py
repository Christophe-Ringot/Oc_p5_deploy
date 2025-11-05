import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.base import BaseEstimator, TransformerMixin


class SafeLogTransform(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.log1p(X)


def safe_log_transform(x):
    return np.log1p(x)

def load_data_from_postgres(db_url: str):
    engine = create_engine(db_url)

    try:
        eval_df = pd.read_sql("SELECT * FROM extrait_eval", engine)
        sirh_df = pd.read_sql("SELECT * FROM extrait_sirh", engine)
        sondage_df = pd.read_sql("SELECT * FROM extrait_sondage", engine)
    finally:
        engine.dispose()

    return eval_df, sirh_df, sondage_df


def preprocess_input(eval_df, sirh_df, sondage_df):

    if eval_df.empty or sirh_df.empty or sondage_df.empty:
        return pd.DataFrame()

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


    eval_df['id_employee'] = eval_df['eval_number'].astype(str).str.extract(r'(\d+)').astype(int)
    sondage_df['id_employee'] = sondage_df['code_sondage'].astype(str).str.extract(r'(\d+)').astype(int)

    full_df = sirh_df.merge(eval_df, on='id_employee', how='inner')\
                     .merge(sondage_df, on='id_employee', how='inner')


    if full_df.empty:
        return pd.DataFrame()


    full_df['augmentation_salaire_precedente'] = full_df['augmentation_salaire_precedente'].apply(
        lambda x: float(str(x).replace(' %', '')) / 100 if isinstance(x, str) else x
    )


    bool_columns = ['heure_supplementaires', 'ayant_enfants']
    for col in bool_columns:
        full_df[col] = full_df[col].apply(lambda x: 1 if x in ['Oui', 'Y'] else 0)

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

    colonnes_a_supprimer = ['eval_number', 'code_sondage']
    if 'a_quitte_l_entreprise' in full_df.columns:
        colonnes_a_supprimer.append('a_quitte_l_entreprise')

    X = full_df.drop(columns=colonnes_a_supprimer)

    return X


def preprocess_single_employee(employee_dict):
    df = pd.DataFrame([employee_dict])

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
