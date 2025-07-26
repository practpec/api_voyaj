from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent))

# Import existing modules
from modules.users.infrastructure.routes.UserRoutes import router as user_router
from modules.friendships.infrastructure.routes.FriendshipRoutes import router as friendship_router
from modules.trips.infrastructure.routes.trip_routes import router as trip_router
from modules.days.infrastructure.routes.day_routes import router as day_router
from modules.activities.infrastructure.routes.activity_routes import router as activity_router
from modules.diary_entries.infrastructure.routes.diary_entry_routes import router as diary_router
from modules.expenses.infrastructure.routes.expense_routes import router as expense_router
from modules.expense_splits.infrastructure.routes.expense_split_routes import router as expense_split_routes
from modules.photos.infrastructure.routes.photo_routes import router as photo_router
from modules.activity_votes.infrastructure.routes.activity_vote_routes import router as activity_vote_routes
from modules.diary_recommendations.infrastructure.routes.diary_recommendation_routes import router as diary_recommendation_router


from shared.database.Connection import DatabaseConnection
from shared.routes.UploadRoutes import router as upload_router
from shared.middleware.ErrorMiddleware import ErrorMiddleware

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[STARTUP] Iniciando Voyaj API...")
    try:
        db = DatabaseConnection()
        await db.connect()
        print("[STARTUP] Conexión a MongoDB establecida")
        yield
    except Exception as e:
        print(f"[ERROR] Error al inicializar: {e}")
        yield
    finally:
        # Shutdown
        try:
            db = DatabaseConnection()
            await db.disconnect()
            print("[SHUTDOWN] Conexión a MongoDB cerrada")
        except:
            pass

app = FastAPI(
    title="Voyaj API",
    description="API REST moderna para gestión de viajes colaborativos",
    version="1.0.0",
    contact={"name": "Voyaj Team", "email": "dev@voyaj.com"},
    license_info={"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add error middleware
app.add_middleware(ErrorMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(user_router, prefix="/api/users", tags=["Usuarios"])
app.include_router(friendship_router, prefix="/api/friendships", tags=["Amistades"])
app.include_router(trip_router, prefix="/api/trips", tags=["Viajes"])
app.include_router(day_router, prefix="/api/days", tags=["Días"])
app.include_router(activity_router, prefix="/api/activities", tags=["Actividades"])
app.include_router(diary_router, prefix="/api/diary", tags=["Diario"])
app.include_router(expense_router, prefix="/api/expenses", tags=["Gastos"])
app.include_router(expense_split_routes, prefix="/api/expenses-split", tags=["Gastos Compartidos"])
app.include_router(photo_router, prefix="/api/photos", tags=["Fotos"])
app.include_router(activity_vote_routes, prefix="/api/activity-votes", tags=["Votos de Actividades"])
app.include_router(diary_recommendation_router, prefix="/api/diary-recommendations", tags=["Recomendaciones de Diario"])
app.include_router(upload_router, tags=["Archivos"])

# Health check endpoint
@app.get("/health", tags=["Sistema"], summary="Health Check")
async def health_check():
    try:
        db = DatabaseConnection()
        await db.connect()
        client = await db.get_client()
        await client.admin.command('ping')
        
        return {
            "status": "healthy",
            "message": "API funcionando correctamente",
            "database": "connected",
            "version": "1.0.0",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "modules": {
                "users": "active",
                "friendships": "active", 
                "trips": "active",
                "days": "active",
                "activities": "active",
                "diary_entries": "active",
                "expenses": "active",
                "expense_splits": "active",
                "photos": "active",
                "activity_votes": "active",
                "diary-recommentations": "active",
                "uploads": "active"
            }
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
@app.get("/", tags=["Sistema"], summary="API Info")
async def root():
    return {
        "message": "Bienvenido a Voyaj API",
        "version": "1.0.0",
        "status": "running",
        "documentation": {"swagger": "/docs", "redoc": "/redoc"},
        "health_check": "/health",
        "endpoints": {
            "users": "/api/users",
            "friendships": "/api/friendships",
            "trips": "/api/trips",
            "days": "/api/days",
            "activities": "/api/activities",
            "diary": "/api/diary",
            "expenses": "/api/expenses",
            "expenses_split": "/api/expenses-split",
            "photos": "/api/photos",
            "activity_votes": "/api/activity-votes",
            "diary_recommendations": "/api/diary-recommendations",
            "uploads": "/api/upload"
        },
        "modules_status": {
            "core": ["users", "trips", "days", "activities","photos", "activity_votes"],
            "social": ["friendships"],
            "content": ["diary_entries", "diary_recommendations"],
            "financial": ["expenses", "expense_splits"],
            "storage": ["uploads"]
        },
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)