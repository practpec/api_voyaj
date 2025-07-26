import os
from pathlib import Path

def create_empty_file(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w'):
        pass  # Archivo completamente vacío

def create_diary_entries_module():
    base_path = "src/modules/diary_entries"
    
    # Root init
    create_empty_file(f"{base_path}/__init__.py")

    # ===== DOMAIN LAYER =====
    create_empty_file(f"{base_path}/domain/__init__.py")
    create_empty_file(f"{base_path}/domain/diary_entry.py")
    create_empty_file(f"{base_path}/domain/diary_entry_events.py")
    create_empty_file(f"{base_path}/domain/diary_entry_service.py")
    
    # Domain Interfaces
    create_empty_file(f"{base_path}/domain/interfaces/__init__.py")
    create_empty_file(f"{base_path}/domain/interfaces/diary_entry_repository.py")

    # ===== APPLICATION LAYER =====
    create_empty_file(f"{base_path}/application/__init__.py")
    
    # DTOs
    create_empty_file(f"{base_path}/application/dtos/__init__.py")
    create_empty_file(f"{base_path}/application/dtos/diary_entry_dto.py")
    
    # Use Cases
    create_empty_file(f"{base_path}/application/use_cases/__init__.py")
    create_empty_file(f"{base_path}/application/use_cases/create_diary_entry.py")
    create_empty_file(f"{base_path}/application/use_cases/get_diary_entry.py")
    create_empty_file(f"{base_path}/application/use_cases/get_day_diary_entries.py")
    create_empty_file(f"{base_path}/application/use_cases/update_diary_entry.py")
    create_empty_file(f"{base_path}/application/use_cases/delete_diary_entry.py")
    create_empty_file(f"{base_path}/application/use_cases/add_emotion.py")
    create_empty_file(f"{base_path}/application/use_cases/get_trip_diary_stats.py")

    # ===== INFRASTRUCTURE LAYER =====
    create_empty_file(f"{base_path}/infrastructure/__init__.py")
    
    # Controllers
    create_empty_file(f"{base_path}/infrastructure/controllers/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/controllers/diary_entry_controller.py")
    
    # Repositories
    create_empty_file(f"{base_path}/infrastructure/repositories/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/repositories/diary_entry_mongo_repository.py")
    
    # Routes
    create_empty_file(f"{base_path}/infrastructure/routes/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/routes/diary_entry_routes.py")

if __name__ == "__main__":
    # Crear desde fuera del directorio src
    if not os.path.exists("src"):
        os.makedirs("src")
    
    create_diary_entries_module()
    print("✅ Módulo diary_entries creado exitosamente con todos los archivos vacíos")