from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
import uuid
from jose import jwt

from database import get_db
from models import User, Sala
from auth import authenticate_user, create_access_token, get_password_hash, verify_password
from schemas import UserCreate, UserLogin, Token
from config import settings

router = APIRouter()

@router.post("/signup", response_class=RedirectResponse)
async def signup(
    request: Request,
    username: str = Form(...),
    correo: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Registrar nuevo usuario"""
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.correo == correo).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )
    
    # Crear nuevo usuario
    hashed_password = get_password_hash(password)
    
    # Generar tokenU como en el backend Node.js
    tokenU = jwt.encode({"newUser": {"username": username, "correo": correo}}, "token_user", algorithm="HS256")
    
    db_user = User(
        username=username,
        correo=correo,
        password=hashed_password,
        tokenU=tokenU
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    
    # Guardar en sesión
    request.session["user_id"] = db_user.id
    request.session["access_token"] = access_token
    
    return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

@router.post("/signin", response_class=RedirectResponse)
async def signin(
    request: Request,
    correo: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Iniciar sesión"""
    # Autenticar usuario
    user = authenticate_user(db, correo, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # Guardar en sesión
    request.session["user_id"] = user.id
    request.session["access_token"] = access_token
    
    return RedirectResponse(url="/profile", status_code=status.HTTP_302_FOUND)

@router.post("/logout", response_class=RedirectResponse)
async def logout(request: Request):
    """Cerrar sesión"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@router.get("/me")
async def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    """Obtener información del usuario actual"""
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "correo": user.correo,
        "created_at": user.created_at
    }