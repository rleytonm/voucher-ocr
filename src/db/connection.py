# src/db/connection.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# 1. Carga .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../config/.env'))

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')

# 2. URL de conexión para MySQL via PyMySQL
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# 3. Engine y Session
engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
    """
    Generador de sesión para usar en scripts o frameworks.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    # Prueba de conexión
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT VERSION();")
            print("MySQL version:", result.scalar())
    except Exception as e:
        print("Error conectando a MySQL:", e)
