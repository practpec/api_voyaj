from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent))

# Import modules
from modules.users.infrastructure.routes.UserRoutes import router as user_router
from shared.database.Connection import DatabaseConnection

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - conexión lazy (solo cuando se necesite)
    print("🚀 Iniciando Voyaj API...")
    try:
        # Inicializar conexión pero sin ping inmediato
        db = DatabaseConnection()
        print("📡 Conexión a MongoDB configurada (lazy loading)")
        yield
    except Exception as e:
        print(f"⚠️ Advertencia al inicializar: {e}")
        yield
    finally:
        # Shutdown
        try:
            db = DatabaseConnection()
            await db.disconnect()
        except:
            pass

app = FastAPI(
    title="Voyaj API",
    description="""
    **Voyaj** es una API REST moderna para gestión de viajes colaborativos.
    
    ## Características principales
    
    * **Gestión de usuarios**: Registro, autenticación y perfiles
    * **Viajes colaborativos**: Creación y gestión de viajes grupales
    * **Subida de archivos**: Fotos de perfil, imágenes de viajes y documentos
    * **Amistades**: Sistema de solicitudes de amistad
    * **Gastos compartidos**: División de gastos entre miembros
    
    ## Autenticación
    
    Esta API utiliza **JWT Bearer tokens** para autenticación.
    
    1. Regístrate con `/api/users/register`
    2. Inicia sesión con `/api/users/login` 
    3. Usa el `access_token` en el header: `Authorization: Bearer <token>`
    
    ## Documentación
    
    * **Swagger UI**: Interfaz interactiva para probar endpoints
    * **ReDoc**: Documentación limpia y detallada en `/redoc`
    """,
    version="1.0.0",
    contact={
        "name": "Voyaj Team",
        "email": "dev@voyaj.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix="/api/users", tags=["👤 Usuarios"])

# Health check endpoint con conexión lazy
@app.get("/health", tags=["🔧 Sistema"], summary="Health Check")
async def health_check():
    """
    Verificar el estado de la API y la base de datos.
    
    Retorna información sobre:
    - Estado de la API
    - Conexión a la base de datos
    - Versión de la aplicación
    """
    try:
        db = DatabaseConnection()
        
        # Intentar conectar solo cuando se llame a health check
        await db.connect()
        client = await db.get_client()
        
        # Ping a la base de datos
        await client.admin.command('ping')
        
        return {
            "status": "healthy",
            "message": "API funcionando correctamente",
            "database": "connected",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": "Error de conectividad con base de datos",
            "database": "disconnected",
            "error": str(e),
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development")
        }

# Root endpoint
@app.get("/", tags=["🔧 Sistema"], summary="API Info")
async def root():
    """
    Información básica de la API.
    
    Endpoint principal que proporciona enlaces a la documentación.
    """
    return {
        "message": "¡Bienvenido a Voyaj API! 🧳✈️",
        "version": "1.0.0",
        "status": "running",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "health_check": "/health",
        "endpoints": {
            "users": "/api/users"
        },
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )