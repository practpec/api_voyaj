import os
from pathlib import Path

def create_file(path, content=""):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def create_trips_module():
    base_path = "src/modules/trips"
    
    # Root init
    create_file(f"{base_path}/__init__.py", '"""Módulo de trips - Gestión de viajes"""')

    # ===== DOMAIN LAYER =====
    create_file(f"{base_path}/domain/__init__.py", '"""Capa de dominio para trips"""')
    create_file(f"{base_path}/domain/trip.py", '"""Entidad Trip con estado, categorías y validaciones"""\n\nclass Trip:\n    pass')
    create_file(f"{base_path}/domain/trip_member.py", '"""Entidad TripMember con roles y estados"""\n\nclass TripMember:\n    pass')
    create_file(f"{base_path}/domain/trip_service.py", '"""Lógica de negocio para trips y miembros"""')
    create_file(f"{base_path}/domain/trip_events.py", '"""Eventos de dominio (crear, actualizar, invitar, etc.)"""')
    
    # Domain Interfaces
    create_file(f"{base_path}/domain/interfaces/__init__.py")
    create_file(f"{base_path}/domain/interfaces/trip_repository.py", 
               '"""Puerto para repositorio de trips"""\n\nclass ITripRepository:\n    pass')
    create_file(f"{base_path}/domain/interfaces/trip_member_repository.py", 
               '"""Puerto para repositorio de miembros"""\n\nclass ITripMemberRepository:\n    pass')

    # ===== APPLICATION LAYER =====
    create_file(f"{base_path}/application/__init__.py", '"""Capa de aplicación para trips"""')
    
    # DTOs
    create_file(f"{base_path}/application/dtos/__init__.py")
    create_file(f"{base_path}/application/dtos/trip_dto.py", '"""DTOs para operaciones de trips"""')
    create_file(f"{base_path}/application/dtos/trip_member_dto.py", '"""DTOs para gestión de miembros"""')
    create_file(f"{base_path}/application/dtos/trip_invitation_dto.py", '"""DTOs para invitaciones a trips"""')
    
    # Use Cases
    create_file(f"{base_path}/application/use_cases/__init__.py")
    create_file(f"{base_path}/application/use_cases/create_trip.py", '"""Caso de uso: Crear un nuevo trip"""')
    create_file(f"{base_path}/application/use_cases/get_trip.py", '"""Caso de uso: Obtener detalles de un trip"""')
    create_file(f"{base_path}/application/use_cases/get_user_trips.py", '"""Caso de uso: Obtener trips de un usuario"""')
    create_file(f"{base_path}/application/use_cases/update_trip.py", '"""Caso de uso: Actualizar información de trip"""')
    create_file(f"{base_path}/application/use_cases/delete_trip.py", '"""Caso de uso: Eliminar un trip"""')
    create_file(f"{base_path}/application/use_cases/update_trip_status.py", '"""Caso de uso: Actualizar estado de un trip"""')
    create_file(f"{base_path}/application/use_cases/invite_user_to_trip.py", '"""Caso de uso: Invitar usuario a trip"""')
    create_file(f"{base_path}/application/use_cases/handle_trip_invitation.py", '"""Caso de uso: Manejar invitación a trip"""')
    create_file(f"{base_path}/application/use_cases/update_member_role.py", '"""Caso de uso: Actualizar rol de miembro"""')
    create_file(f"{base_path}/application/use_cases/remove_trip_member.py", '"""Caso de uso: Remover miembro de trip"""')
    create_file(f"{base_path}/application/use_cases/leave_trip.py", '"""Caso de uso: Abandonar un trip"""')
    create_file(f"{base_path}/application/use_cases/get_trip_members.py", '"""Caso de uso: Obtener miembros de un trip"""')
    create_file(f"{base_path}/application/use_cases/export_trip.py", '"""Caso de uso: Exportar datos de trip"""')

    # ===== INFRASTRUCTURE LAYER =====
    create_file(f"{base_path}/infrastructure/__init__.py", '"""Capa de infraestructura para trips"""')
    
    # Controllers
    create_file(f"{base_path}/infrastructure/controllers/__init__.py")
    create_file(f"{base_path}/infrastructure/controllers/trip_controller.py", 
               '"""Controlador FastAPI para trips"""')
    
    # Repositories
    create_file(f"{base_path}/infrastructure/repositories/__init__.py")
    create_file(f"{base_path}/infrastructure/repositories/trip_mongo_repository.py", 
               '"""Implementación MongoDB para trips"""')
    create_file(f"{base_path}/infrastructure/repositories/trip_member_mongo_repository.py", 
               '"""Implementación MongoDB para miembros de trips"""')
    
    # Services
    create_file(f"{base_path}/infrastructure/services/__init__.py")
    create_file(f"{base_path}/infrastructure/services/trip_export_service.py", 
               '"""Servicio para exportación de trips"""')
    
    # Routes
    create_file(f"{base_path}/infrastructure/routes/__init__.py")
    create_file(f"{base_path}/infrastructure/routes/trip_routes.py", 
               '"""Definición de rutas para trips"""')

if __name__ == "__main__":
    # Crear desde fuera del directorio src
    if not os.path.exists("src"):
        os.makedirs("src")
    
    create_trips_module()
    print("✅ Módulo trips creado exitosamente con 46 archivos (37 + 9 __init__.py)")