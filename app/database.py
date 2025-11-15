from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Détecter l'environnement Hugging Face ou utiliser SQLite par défaut
SPACE_ID = os.getenv('SPACE_ID')  # Variable spécifique à Hugging Face Spaces
POSTGRES_USER = os.getenv("POSTGRES_USER")
DB_PORT = os.getenv('DB_PORT')

# Utiliser SQLite si on est sur Hugging Face ou si PostgreSQL n'est pas configuré
if SPACE_ID or not POSTGRES_USER or not DB_PORT:
    # Environnement Hugging Face ou PostgreSQL non configuré -> utiliser SQLite
    DATABASE_URL = "sqlite:///./app.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    print("🔧 Utilisation de SQLite (Hugging Face ou environnement sans PostgreSQL)")
else:
    # PostgreSQL configuré (local/CI)
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print(f"🔧 Utilisation de PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
