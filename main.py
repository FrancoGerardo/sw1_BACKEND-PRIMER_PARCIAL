from app import app
from database import create_tables
from routes import auth_routes, salas_routes, web_routes
import uvicorn

if __name__ == "__main__":
    # Incluir rutas
    app.include_router(auth_routes.router, prefix="/api/auth", tags=["authentication"])
    app.include_router(salas_routes.router, prefix="/api/salas", tags=["salas"])
    app.include_router(web_routes.router, tags=["web"])
    
    # Crear tablas en la base de datos
    create_tables()
    
    # Ejecutar la aplicación
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)