from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Settings(BaseSettings):
    # Configuración de la base de datos
    #DB_HOST: str = os.getenv("DB_HOST", "localhost")
    #DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    #DB_USER: str = os.getenv("DB_USER", "postgres")
    #DB_PASSWORD: str = os.getenv("DB_PASSWORD", "root")
    #DB_NAME: str = os.getenv("DB_NAME", "parcialsw")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:dpBoVbqnIggkFsgZlfCYIqIAPIyXJrfK@maglev.proxy.rlwy.net:39379/railway")


    # Configuración JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # URL de la base de datos
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Crear instancia de configuración
settings = Settings()