from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

# Crear motor de base de datos
engine = create_engine(settings.DATABASE_URL)

# Crear sesión de base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Crear tablas en la base de datos"""
    # Importar modelos para que se registren
    from models import User, Sala, UserSala
    Base.metadata.create_all(bind=engine)