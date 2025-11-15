"""
Script d'initialisation de la base de données pour l'environnement de déploiement (Hugging Face).
Ce script crée les tables nécessaires et charge les données CSV.
"""
import pandas as pd
from sqlalchemy import Table, Column, Integer, Float, String, DateTime, JSON, MetaData
from sqlalchemy.sql import func
from app.database import engine, Base
from app.models import Prediction
import os

def init_database():
    """
    Initialise la base de données en créant les tables et en chargeant les données CSV.
    Compatible avec SQLite (Hugging Face) et PostgreSQL (local).
    """
    try:
        # 1. Créer toutes les tables définies dans les modèles (comme Prediction)
        print("Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables des modèles créées")

        # 2. Vérifier si les données CSV existent
        csv_files = {
            'sirh': './data/extrait_sirh.csv',
            'eval': './data/extrait_eval.csv',
            'sondage': './data/extrait_sondage.csv'
        }

        missing_files = [name for name, path in csv_files.items() if not os.path.exists(path)]
        if missing_files:
            print(f"⚠ Fichiers CSV manquants: {', '.join(missing_files)}")
            print("Les tables de données ne seront pas créées.")
            return

        # 3. Charger les données CSV dans la base de données
        print("Chargement des données CSV...")

        df_sirh = pd.read_csv(csv_files['sirh'])
        df_eval = pd.read_csv(csv_files['eval'])
        df_sondage = pd.read_csv(csv_files['sondage'])

        # Remplacer les tables existantes (if_exists='replace')
        df_sirh.to_sql('extrait_sirh', engine, if_exists='replace', index=False)
        print(f"✓ Table 'extrait_sirh' créée avec {len(df_sirh)} lignes")

        df_eval.to_sql('extrait_eval', engine, if_exists='replace', index=False)
        print(f"✓ Table 'extrait_eval' créée avec {len(df_eval)} lignes")

        df_sondage.to_sql('extrait_sondage', engine, if_exists='replace', index=False)
        print(f"✓ Table 'extrait_sondage' créée avec {len(df_sondage)} lignes")

        print("✅ Base de données initialisée avec succès !")

    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la base de données: {e}")
        raise

if __name__ == "__main__":
    init_database()
