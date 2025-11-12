import pandas as pd
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON, Table, MetaData
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

# Utiliser SQLite pour Hugging Face Spaces, PostgreSQL en local/CI
if os.getenv("SPACE_ID"):
    connection_string = "sqlite:///./app.db"
else:
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT'))
    DB_NAME = os.getenv('DB_NAME')
    connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

def create_database():
    try:
        if os.getenv("SPACE_ID"):
            engine = create_engine(connection_string, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(connection_string)
        metadata = MetaData()

        predictions_table = Table(
            'predictions',
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True),
            Column('employee_id', Integer),
            Column('prediction', Integer),
            Column('probability', Float),
            Column('probabilities', JSON),
            Column('created_at', DateTime(timezone=True), server_default=func.now())
        )

        metadata.create_all(engine)

        df_sirh = pd.read_csv('./data/extrait_sirh.csv')
        df_eval = pd.read_csv('./data/extrait_eval.csv')
        df_sondage = pd.read_csv('./data/extrait_sondage.csv')

        df_sirh.to_sql('extrait_sirh', engine, if_exists='replace', index=False)

        df_eval.to_sql('extrait_eval', engine, if_exists='replace', index=False)

        df_sondage.to_sql('extrait_sondage', engine, if_exists='replace', index=False)
        print("Tables créées avec succès")

    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    create_database()
