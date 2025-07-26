import os
from pathlib import Path

def create_empty_file(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w'):
        pass  # Archivo completamente vacío

def create_expenses_module():
    base_path = "src/modules/expenses"
    
    # Root init
    create_empty_file(f"{base_path}/__init__.py")

    # ===== DOMAIN LAYER =====
    create_empty_file(f"{base_path}/domain/__init__.py")
    create_empty_file(f"{base_path}/domain/expense.py")
    create_empty_file(f"{base_path}/domain/expense_service.py")
    create_empty_file(f"{base_path}/domain/expense_events.py")
    
    # Domain Interfaces
    create_empty_file(f"{base_path}/domain/interfaces/__init__.py")
    create_empty_file(f"{base_path}/domain/interfaces/expense_repository_interface.py")

    # ===== APPLICATION LAYER =====
    create_empty_file(f"{base_path}/application/__init__.py")
    
    # DTOs
    create_empty_file(f"{base_path}/application/dtos/__init__.py")
    create_empty_file(f"{base_path}/application/dtos/create_expense_dto.py")
    create_empty_file(f"{base_path}/application/dtos/update_expense_dto.py")
    
    # Use Cases
    create_empty_file(f"{base_path}/application/use_cases/__init__.py")
    create_empty_file(f"{base_path}/application/use_cases/create_expense.py")
    create_empty_file(f"{base_path}/application/use_cases/update_expense.py")
    create_empty_file(f"{base_path}/application/use_cases/delete_expense.py")
    create_empty_file(f"{base_path}/application/use_cases/get_expense.py")
    create_empty_file(f"{base_path}/application/use_cases/get_trip_expenses.py")

    # ===== INFRASTRUCTURE LAYER =====
    create_empty_file(f"{base_path}/infrastructure/__init__.py")
    
    # Controllers
    create_empty_file(f"{base_path}/infrastructure/controllers/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/controllers/expense_controller.py")
    
    # Repositories
    create_empty_file(f"{base_path}/infrastructure/repositories/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/repositories/expense_mongo_repository.py")
    
    # Routes
    create_empty_file(f"{base_path}/infrastructure/routes/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/routes/expense_routes.py")
    
    # Events
    create_empty_file(f"{base_path}/infrastructure/events/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/events/expense_notification_handler.py")
    
    # Services
    create_empty_file(f"{base_path}/infrastructure/services/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/services/budget_tracking_service.py")
    
    # Factories
    create_empty_file(f"{base_path}/infrastructure/factories/__init__.py")
    create_empty_file(f"{base_path}/infrastructure/factories/expense_factory.py")

if __name__ == "__main__":
    # Crear desde fuera del directorio src
    if not os.path.exists("src"):
        os.makedirs("src")
    
    create_expenses_module()
    print("✅ Módulo expenses creado exitosamente con todos los archivos vacíos")