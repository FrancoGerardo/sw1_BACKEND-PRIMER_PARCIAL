from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from database import get_db
from models import User, Sala, UserSala

router = APIRouter()

async def get_current_user_from_session(request: Request, db: Session = Depends(get_db)):
    """Obtener usuario actual desde la sesión"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user

@router.get("/api/user/{tokenU}")
async def get_user_by_token(tokenU: str, db: Session = Depends(get_db)):
    """Obtener usuario por token"""
    user = db.query(User).filter(User.id == int(tokenU)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {
        "id": user.id,
        "username": user.username,
        "correo": user.correo
    }

@router.get("/api/guardar-diagrama/{tokenS}")
async def save_diagram(tokenS: str, xml: str, db: Session = Depends(get_db)):
    """Guardar diagrama XML"""
    sala = db.query(Sala).filter(Sala.tokenS == tokenS).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    sala.xml = xml
    db.commit()
    
    return {"message": "Diagrama guardado exitosamente"}

@router.get("/api/cargar-salas/{tokenS}")
async def load_rooms(tokenS: str, db: Session = Depends(get_db)):
    """Cargar salas del usuario"""
    # Buscar usuario por tokenS (asumiendo que tokenS es el ID del usuario)
    user = db.query(User).filter(User.id == int(tokenS)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener salas del usuario
    salas = db.query(Sala).filter(Sala.user_id == user.id).all()
    
    return [{
        "id": sala.id,
        "title": sala.title,
        "description": sala.description,
        "xml": sala.xml,
        "tokenS": sala.tokenS,
        "created_at": sala.created_at
    } for sala in salas]