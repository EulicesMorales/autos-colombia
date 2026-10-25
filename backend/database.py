from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Reemplaza 'tu_contraseña' por tu clave de PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://postgres:admin@localhost/autos_colombia"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()