# Backend Python - UML Diagrammer

Este es el backend Python que replica exactamente la funcionalidad del backend Node.js original, incluyendo todas las vistas HTML y el sistema de autenticación.

## 🚀 Características

- **FastAPI** como framework web
- **Jinja2** para templates HTML
- **PostgreSQL** como base de datos
- **SQLAlchemy** como ORM
- **Sesiones** para autenticación
- **JWT** para tokens de API
- **Templates HTML** idénticos al original

## 📁 Estructura

```
Backend_python/
├── app.py                 # Aplicación principal
├── auth.py                # Sistema de autenticación
├── config.py              # Configuración
├── database.py            # Configuración de BD
├── models.py              # Modelos SQLAlchemy
├── schemas.py             # Esquemas Pydantic
├── requirements.txt       # Dependencias
├── env_example.txt        # Variables de entorno
├── routes/                # Módulos de rutas
│   ├── auth_routes.py     # Rutas de autenticación
│   ├── salas_routes.py    # Rutas de salas
│   └── web_routes.py      # Rutas web
├── templates/             # Templates HTML
│   ├── base.html          # Layout base
│   ├── index.html         # Página principal
│   ├── welcome.html       # Página de bienvenida
│   ├── auth/              # Templates de auth
│   │   ├── signin.html    # Login
│   │   └── signup.html    # Registro
│   ├── salas/             # Templates de salas
│   │   ├── list.html      # Lista de salas
│   │   ├── add.html       # Crear sala
│   │   ├── edit.html      # Editar sala
│   │   ├── listUsuarios.html # Compartir sala
│   │   └── listCompartidas.html # Salas compartidas
│   └── partitials/        # Partes reutilizables
│       ├── navigation.html # Navegación
│       └── message.html   # Mensajes
└── static/               # Archivos estáticos
    ├── css/              # Estilos CSS
    └── img/              # Imágenes
```

## 🛠️ Instalación

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
cp env_example.txt .env
# Editar .env con tus credenciales
```

3. **Ejecutar la aplicación:**
```bash
python main.py
```

## 🌐 URLs Disponibles

### Páginas Web
- `/` - Página principal
- `/signin` - Login
- `/signup` - Registro
- `/profile` - Perfil del usuario
- `/salas` - Lista de salas
- `/salas/add` - Crear sala
- `/salas/edit/{id}` - Editar sala
- `/salas/delete/{id}` - Eliminar sala
- `/salas/inSala/{tokenS}` - Entrar a sala
- `/salas/listUsuarios/{id}` - Compartir sala
- `/salas/salasCompartidas` - Salas compartidas

### APIs REST
- `/api/auth/signup` - POST - Registro
- `/api/auth/signin` - POST - Login
- `/api/auth/logout` - POST - Logout
- `/api/auth/me` - GET - Usuario actual
- `/api/salas/add` - POST - Crear sala
- `/api/salas/edit/{id}` - POST - Editar sala
- `/api/salas/{id}` - GET - Obtener sala
- `/api/salas/token/{tokenS}` - GET - Obtener sala por token
- `/api/salas/share/{id}` - POST - Compartir sala
- `/api/salas/share/{id}/{user_id}` - DELETE - Dejar de compartir
- `/api/user/{tokenU}` - GET - Usuario por token
- `/api/guardar-diagrama/{tokenS}` - GET - Guardar diagrama
- `/api/cargar-salas/{tokenS}` - GET - Cargar salas

## 🔧 Configuración

### Variables de Entorno
```env
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=root
DB_NAME=parcialsw

# JWT
SECRET_KEY=your-secret-key-here

# Aplicación
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## 🗄️ Base de Datos

El sistema usa PostgreSQL con las siguientes tablas:

- **users** - Usuarios del sistema
- **salas** - Salas/diagramas
- **userSalas** - Relación usuarios-salas (compartir)

## 🔐 Autenticación

- **Sesiones** para páginas web
- **JWT** para APIs REST
- **Bcrypt** para hash de contraseñas
- **Middleware** de autenticación

## 🎨 Frontend

El frontend se mantiene igual que el original, solo se adapta la comunicación WebSocket para trabajar con FastAPI.

## 📝 Notas

- Este backend replica **exactamente** la funcionalidad del Node.js original
- Mantiene la misma experiencia de usuario
- Compatible con el frontend existente
- Mejor rendimiento con Python/FastAPI