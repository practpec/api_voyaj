import os
from pathlib import Path

def create_file(path, content=""):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def create_friendships_module():
    base_path = "src/modules/friendships"
    
    # Domain layer
    create_file(f"{base_path}/__init__.py")
    create_file(f"{base_path}/domain/__init__.py")
    create_file(f"{base_path}/domain/friendship.py", '"""Entidad Friendship"""\n\nclass Friendship:\n    pass')
    create_file(f"{base_path}/domain/friendship_events.py", '"""Eventos de dominio para friendships"""')
    create_file(f"{base_path}/domain/friendship_service.py", '"""Servicio de dominio para friendships"""')
    create_file(f"{base_path}/domain/interfaces/__init__.py")
    create_file(f"{base_path}/domain/interfaces/friendship_repository.py", '"""Interfaz del repositorio para friendships"""\n\nclass IFriendshipRepository:\n    pass')

    # Application layer
    create_file(f"{base_path}/application/__init__.py")
    create_file(f"{base_path}/application/dtos/__init__.py")
    create_file(f"{base_path}/application/dtos/friendship_dto.py", '"""DTOs para friendships"""')
    create_file(f"{base_path}/application/use_cases/__init__.py")
    create_file(f"{base_path}/application/use_cases/send_friend_request.py", '"""Caso de uso: enviar solicitud de amistad"""')
    create_file(f"{base_path}/application/use_cases/accept_friend_request.py", '"""Caso de uso: aceptar solicitud de amistad"""')
    create_file(f"{base_path}/application/use_cases/reject_friend_request.py", '"""Caso de uso: rechazar solicitud de amistad"""')
    create_file(f"{base_path}/application/use_cases/remove_friendship.py", '"""Caso de uso: eliminar amistad"""')
    create_file(f"{base_path}/application/use_cases/get_friends.py", '"""Caso de uso: obtener lista de amigos"""')
    create_file(f"{base_path}/application/use_cases/get_friend_requests.py", '"""Caso de uso: obtener solicitudes pendientes"""')
    create_file(f"{base_path}/application/use_cases/get_friend_suggestions.py", '"""Caso de uso: obtener sugerencias de amigos"""')
    create_file(f"{base_path}/application/use_cases/get_friendship_stats.py", '"""Caso de uso: obtener estadísticas de amistad"""')

    # Infrastructure layer
    create_file(f"{base_path}/infrastructure/__init__.py")
    create_file(f"{base_path}/infrastructure/controllers/__init__.py")
    create_file(f"{base_path}/infrastructure/controllers/friendship_controller.py", '"""Controlador HTTP para friendships"""')
    create_file(f"{base_path}/infrastructure/repositories/__init__.py")
    create_file(f"{base_path}/infrastructure/repositories/friendship_mongo_repository.py", '"""Implementación MongoDB para el repositorio"""')
    create_file(f"{base_path}/infrastructure/events/__init__.py")
    create_file(f"{base_path}/infrastructure/events/friendship_notification_handler.py", '"""Manejador de eventos para notificaciones de amistad"""')

if __name__ == "__main__":
    # Crear desde fuera del directorio src
    if not os.path.exists("src"):
        os.makedirs("src")
    
    create_friendships_module()
    print("✅ Módulo friendships creado exitosamente con todos los archivos y __init__.py")