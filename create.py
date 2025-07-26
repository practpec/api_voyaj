import os
from pathlib import Path

def create_empty_file(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w'):
        pass  # Archivo completamente vacío

def create_activities_module():
    base_path = "src/modules/activities"
    
    # Root init
    create_empty_file(f"{base_path}/__init__.py")

    # ===== DOMAIN LAYER =====
    create_empty_file(f"{base_path}/domain/__init__.py")
    create_empty_file(f"{base_path}/domain/activity.py")
    create_empty_file(f"{base_path}/domain/activity_events.py")
    create_empty_file(f"{base_path}/domain/activity_service.py")
    
    # Domain Interfaces
    create_empty_file(f"{base_path}/domain/interfaces/__init__.py")
    create_empty_file(f"{base_path}/domain/interfaces/activity_repository.py")

    # ===== APPLICATION LAYER =====
    create_empty_file(f"{base_path}/application/__init__.py")
    
    # DTOs
    create_empty_file(f"{base_path}/application/dtos/__init__.py")
    create_empty_file(f"{base_path}/application/dtos/activity_dto.py")
    
    # Response DTOs
    create_empty_file(f"{base_path}/application/dtos/responses/__init__.py")
    create_empty_file(f"{base_path}/application/dtos/responses/activity_response.py")
    create_empty_file(f"{base_path}/application/dtos/responses/day_activities_response.py")
    create_empty_file(f"{base_path}/application/dtos/responses/reorder_response.py")
    
    # Use Cases
    create_empty_file(f"{base_path}/application/use_cases/__init__.py")
    create_empty_file(f"{base_path}/application/use_cases/create_activity.py")
    create_empty_file(f"{base_path}/application/use_cases/get_activity.py")
    create_empty_file(f"{base_path}/application/use_cases/get_day_activities.py")
    create_empty_file(f"{base_path}/application/use_cases/update_activity.py")
    create_empty_file(f"{base_path}/application/use_cases/change_activity_status.py")
    create_empty_file(f"{base_path}/application/use_cases/reorder_activities.py")
    create_empty_file(f"{base_path}/application/use_cases/delete_activity.py")

    # ===== INFRASTRUCTURE LAYER =====
    create_empty_file(f"{base_path}/infrastructure/__init__.py")
    
    # Controllers
    create_empty_file(f"{base_path}/infrastructure/controllers/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/controllers/activity_controller.py")
    
    # Repositories
    create_empty_file(f"{base_path}/infrastructure/repositories/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/repositories/activity_mongo_repository.py")
    
    # Routes
    create_empty_file(f"{base_path}/infrastructure/routes/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/routes/activity_routes.py")

if __name__ == "__main__":
    # Crear desde fuera del directorio src
    if not os.path.exists("src"):
        os.makedirs("src")
    
    create_activities_module()
    print("✅ Módulo activities creado exitosamente con todos los archivos vacíos")