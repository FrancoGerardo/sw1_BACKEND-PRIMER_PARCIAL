from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# Crear aplicación FastAPI
app = FastAPI(title="UML Diagrammer Backend", version="1.0.0")

# Ruta raíz
@app.get("/", response_class=HTMLResponse)
async def index():
    """Página principal"""
    return """
    <html>
        <head>
            <title>Diagramador UML API</title>
        </head>
        <body>
            <h1>Diagramador UML API</h1>
            <p>API funcionando correctamente</p>
            <a href="/docs">Ver documentación de la API</a>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
