from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import uuid

from database import get_db
from models import User, Sala, UserSala
from auth import get_current_user_from_session
from schemas import SalaCreate, SalaUpdate

router = APIRouter()

async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Obtener usuario actual desde sesión"""
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
    return user

@router.post("/add", response_class=RedirectResponse)
async def create_sala(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    xml: str = Form(""),
    db: Session = Depends(get_db)
):
    """Crear nueva sala"""
    user = await get_current_user(request, db)
    
    # Generar token único para la sala
    tokenS = str(uuid.uuid4())
    
    # Crear nueva sala
    db_sala = Sala(
        title=title,
        description=description,
        xml=xml,
        tokenS=tokenS,
        user_id=user.id
    )
    db.add(db_sala)
    db.commit()
    db.refresh(db_sala)
    
    # Insertar automáticamente al creador en userSalas (como en Node.js)
    db_user_sala = UserSala(
        user_id=user.id,
        salas_id=db_sala.id
    )
    db.add(db_user_sala)
    db.commit()
    
    return RedirectResponse(url="/salas", status_code=status.HTTP_302_FOUND)

@router.post("/edit/{sala_id}", response_class=RedirectResponse)
async def update_sala(
    request: Request,
    sala_id: int,
    title: str = Form(...),
    description: str = Form(""),
    xml: str = Form(""),
    db: Session = Depends(get_db)
):
    """Actualizar sala existente"""
    user = await get_current_user(request, db)
    
    # Verificar que la sala pertenece al usuario
    sala = db.query(Sala).filter(Sala.id == sala_id, Sala.user_id == user.id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    # Actualizar sala
    sala.title = title
    sala.description = description
    sala.xml = xml
    db.commit()
    
    return RedirectResponse(url="/salas", status_code=status.HTTP_302_FOUND)

@router.get("/{sala_id}")
async def get_sala(sala_id: int, db: Session = Depends(get_db)):
    """Obtener sala por ID"""
    sala = db.query(Sala).filter(Sala.id == sala_id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return sala

@router.get("/token/{tokenS}")
async def get_sala_by_token(tokenS: str, db: Session = Depends(get_db)):
    """Obtener sala por token"""
    sala = db.query(Sala).filter(Sala.tokenS == tokenS).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return sala

@router.post("/share/{sala_id}")
async def share_sala(
    request: Request,
    sala_id: int,
    idUsuario: int = Form(...),
    db: Session = Depends(get_db)
):
    """Compartir sala con otro usuario (como en Node.js)"""
    user = await get_current_user(request, db)
    
    # Verificar que la sala pertenece al usuario
    sala = db.query(Sala).filter(Sala.id == sala_id, Sala.user_id == user.id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    # Verificar que no sea el mismo usuario
    if idUsuario == user.id:
        raise HTTPException(status_code=400, detail="No puedes compartir contigo mismo")
    
    # Verificar que no esté ya compartida
    existing_share = db.query(UserSala).filter(
        UserSala.salas_id == sala_id,
        UserSala.user_id == idUsuario
    ).first()
    if existing_share:
        raise HTTPException(status_code=400, detail="La sala ya está compartida con este usuario")
    
    # Crear compartir (como en Node.js)
    db_share = UserSala(
        user_id=idUsuario,
        salas_id=sala_id
    )
    db.add(db_share)
    db.commit()
    
    return RedirectResponse(url=f"/salas/listUsuarios/{sala_id}", status_code=status.HTTP_302_FOUND)

@router.delete("/share/{sala_id}/{user_id}")
async def unshare_sala(
    request: Request,
    sala_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """Dejar de compartir sala"""
    user = await get_current_user(request, db)
    
    # Verificar que la sala pertenece al usuario
    sala = db.query(Sala).filter(Sala.id == sala_id, Sala.user_id == user.id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    # Eliminar compartir
    share = db.query(UserSala).filter(
        UserSala.salas_id == sala_id,
        UserSala.user_id == user_id
    ).first()
    if not share:
        raise HTTPException(status_code=404, detail="Compartir no encontrado")
    
    db.delete(share)
    db.commit()
    
    return {"message": "Sala dejada de compartir exitosamente"}