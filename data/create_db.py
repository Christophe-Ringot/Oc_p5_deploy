import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_NAME = os.getenv('DB_NAME')


connection_string = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

def create_database():
    try:
        engine = create_engine(connection_string)
        
        df_sirh = pd.read_csv('./data/extrait_sirh.csv')
        df_eval = pd.read_csv('./data/extrait_eval.csv')
        df_sondage = pd.read_csv('./data/extrait_sondage.csv')

        df_sirh.to_sql('employee_sirh', engine, if_exists='replace', index=False)

        df_eval.to_sql('employee_evaluations', engine, if_exists='replace', index=False)

        df_sondage.to_sql('employee_survey', engine, if_exists='replace', index=False)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    create_database()
