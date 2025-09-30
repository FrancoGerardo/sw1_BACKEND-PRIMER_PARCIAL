from fastapi import FastAPI, Request, Depends, HTTPException, status, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

# Importar módulos locales
from database import get_db
from models import User, Sala, UserSala

# Cargar variables de entorno
load_dotenv()

# Crear aplicación FastAPI
app = FastAPI(title="UML Diagrammer Backend", version="1.0.0")

# Configurar middleware de sesiones
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-here"),
    max_age=86400,  # 24 horas
    same_site="lax"
)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir rutas
from routes import auth_routes, salas_routes, web_routes
app.include_router(auth_routes.router, prefix="/api/auth", tags=["authentication"])
app.include_router(salas_routes.router, prefix="/api/salas", tags=["salas"])
app.include_router(web_routes.router, tags=["web"])

# Función para obtener el usuario actual desde la sesión
async def get_current_user_from_session(request: Request, db: Session = Depends(get_db)):
    """Obtiene el usuario actual desde la sesión"""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user

# Función para verificar si el usuario está autenticado
async def require_auth(request: Request, db: Session = Depends(get_db)):
    """Middleware para requerir autenticación"""
    user = await get_current_user_from_session(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado"
        )
    return user

# Función para verificar si el usuario NO está autenticado
async def require_no_auth(request: Request):
    """Middleware para páginas que requieren que el usuario NO esté autenticado"""
    user_id = request.session.get("user_id")
    if user_id:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            detail="Ya estás autenticado"
        )

# Ruta raíz
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    """Página principal"""
    user = await get_current_user_from_session(request, db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user
    })

# Ruta de login
@app.get("/signin", response_class=HTMLResponse)
async def signin_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("auth/signin.html", {
        "request": request
    })

# Ruta de registro
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Página de registro"""
    return templates.TemplateResponse("auth/signup.html", {
        "request": request
    })

# Ruta de perfil
@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    """Página de perfil del usuario"""
    user = await require_auth(request, db)
    return templates.TemplateResponse("welcome.html", {
        "request": request,
        "user": user
    })

# Ruta de logout
@app.get("/logout")
async def logout(request: Request):
    """Cerrar sesión"""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

# Ruta de salas
@app.get("/salas", response_class=HTMLResponse)
async def salas_page(request: Request, db: Session = Depends(get_db)):
    """Página de lista de salas"""
    user = await require_auth(request, db)
    
    # Obtener salas del usuario
    salas = db.query(Sala).filter(Sala.user_id == user.id).all()
    
    return templates.TemplateResponse("salas/list.html", {
        "request": request,
        "user": user,
        "salas": salas
    })

# Ruta para crear sala
@app.get("/salas/add", response_class=HTMLResponse)
async def add_sala_page(request: Request, db: Session = Depends(get_db)):
    """Página para crear nueva sala"""
    user = await require_auth(request, db)
    return templates.TemplateResponse("salas/add.html", {
        "request": request,
        "user": user
    })

# Ruta para editar sala
@app.get("/salas/edit/{sala_id}", response_class=HTMLResponse)
async def edit_sala_page(request: Request, sala_id: int, db: Session = Depends(get_db)):
    """Página para editar sala"""
    user = await require_auth(request, db)
    
    # Verificar que la sala pertenece al usuario
    sala = db.query(Sala).filter(Sala.id == sala_id, Sala.user_id == user.id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    return templates.TemplateResponse("salas/edit.html", {
        "request": request,
        "user": user,
        "sala": sala
    })

# Ruta para eliminar sala
@app.get("/salas/delete/{sala_id}")
async def delete_sala(request: Request, sala_id: int, db: Session = Depends(get_db)):
    """Eliminar sala"""
    user = await require_auth(request, db)
    
    # Verificar que la sala pertenece al usuario
    sala = db.query(Sala).filter(Sala.id == sala_id, Sala.user_id == user.id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    # Eliminar la sala
    db.delete(sala)
    db.commit()
    
    return RedirectResponse(url="/salas", status_code=status.HTTP_302_FOUND)

# Ruta para entrar a una sala
@app.get("/salas/inSala/{tokenS}")
async def enter_sala(request: Request, tokenS: str, db: Session = Depends(get_db)):
    """Entrar a una sala específica"""
    user = await require_auth(request, db)
    
    # Buscar la sala por token
    sala = db.query(Sala).filter(Sala.tokenS == tokenS).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    # Redirigir al frontend con el token
    # frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8081") + f"/model-UML?room={tokenS}&username={user.tokenU}"
    # frontend_url = os.getenv("FRONTEND_URL", "https://tu-frontend.railway.app") + f"/model-UML?room={tokenS}&username={user.tokenU}"
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8081") + f"/model-UML?room={tokenS}&username={user.tokenU}"
    return RedirectResponse(url=frontend_url, status_code=status.HTTP_302_FOUND)

# Ruta para compartir sala
@app.get("/salas/listUsuarios/{sala_id}", response_class=HTMLResponse)
async def share_sala_page(request: Request, sala_id: int, db: Session = Depends(get_db)):
    """Página para compartir sala (como en Node.js)"""
    user = await require_auth(request, db)
    
    # Verificar que la sala pertenece al usuario
    sala = db.query(Sala).filter(Sala.id == sala_id, Sala.user_id == user.id).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    # Obtener TODOS los usuarios disponibles (como en Node.js)
    users = db.query(User).all()
    
    return templates.TemplateResponse("salas/listUsuarios.html", {
        "request": request,
        "user": user,
        "sala": sala,
        "users": users,
        "idSala": sala_id
    })

# Ruta para salas compartidas
@app.get("/salas/salasCompartidas", response_class=HTMLResponse)
async def shared_salas_page(request: Request, db: Session = Depends(get_db)):
    """Página de salas compartidas"""
    user = await require_auth(request, db)
    
    # Obtener salas compartidas con el usuario
    user_salas = db.query(UserSala).filter(UserSala.user_id == user.id).all()
    salas = []
    for us in user_salas:
        sala = db.query(Sala).filter(Sala.id == us.salas_id).first()
        if sala:
            salas.append(sala)
    
    return templates.TemplateResponse("salas/listCompartidas.html", {
        "request": request,
        "user": user,
        "salas": salas
    })

# Importar WebSocket manager
from websocket_manager import websocket_endpoint

# Rutas de API para el frontend
@app.get("/apis/user/{tokenU}")
async def get_user_by_token(tokenU: str, db: Session = Depends(get_db)):
    """Obtener usuario por token (para compatibilidad con frontend)"""
    user = db.query(User).filter(User.tokenU == tokenU).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "name": user.username,
        "email": user.correo,
        "token": user.tokenU
    }

@app.get("/apis/cargar-salas/{tokenS}")
async def get_sala_by_token_api(tokenS: str, db: Session = Depends(get_db)):
    """Obtener sala por token (para compatibilidad con frontend)"""
    sala = db.query(Sala).filter(Sala.tokenS == tokenS).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    return {
        "id": sala.id,
        "nombre": sala.title,
        "descripcion": sala.description,
        "user_id": sala.user_id,
        "content": sala.xml or "",
        "codigo": sala.tokenS
    }

@app.put("/apis/guardar-diagrama/{tokenS}")
async def save_diagram(tokenS: str, content: dict, db: Session = Depends(get_db)):
    """Guardar diagrama (para compatibilidad con frontend)"""
    sala = db.query(Sala).filter(Sala.tokenS == tokenS).first()
    if not sala:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    
    # Actualizar el XML de la sala
    sala.xml = content.get("content", "")
    db.commit()
    
    return {"status": "Project Updated Successfully"}

# Ruta de WebSocket para comunicación en tiempo real
@app.websocket("/ws/{room}/{username}")
async def websocket_route(websocket: WebSocket, room: str, username: str):
    await websocket_endpoint(websocket, room, username)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)