from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os
from dotenv import load_dotenv

from database import get_db
from models import User

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto de contraseñas
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Esquema de autenticación
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Obtener hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verificar token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def authenticate_user(db: Session, correo: str, password: str) -> Optional[User]:
    """Autenticar usuario"""
    user = db.query(User).filter(User.correo == correo).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """Obtener usuario actual desde token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

def get_user_by_correo(db: Session, correo: str) -> Optional[User]:
    """Obtener usuario por correo"""
    return db.query(User).filter(User.correo == correo).first()

def create_user(db: Session, username: str, correo: str, password: str) -> User:
    """Crear nuevo usuario"""
    hashed_password = get_password_hash(password)
    db_user = User(
        username=username,
        correo=correo,
        password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_current_user_from_session(request, db: Session = Depends(get_db)) -> Optional[User]:
    """Obtener usuario actual desde la sesión"""
    from fastapi import Request
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user