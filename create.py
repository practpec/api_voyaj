import os
from pathlib import Path

def create_file(path, content=""):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def create_project_structure():
    # Main file
    create_file("src/main.py", '"""Punto de entrada de la aplicación"""\n\nprint("Hello World!")')
    
    # Users module
    create_file("src/modules/users/domain/User.py", '"""Entidad de usuario"""\n\nclass User:\n    pass')
    create_file("src/modules/users/domain/interfaces/IUserRepository.py", '"""Interfaz para el repositorio de usuarios"""\n\nclass IUserRepository:\n    pass')
    
    # Application layer
    create_file("src/modules/users/application/dtos/UserDTOs.py", '"""DTOs para el módulo de usuarios"""')
    create_file("src/modules/users/application/useCases/CreateUser.py", '"""Caso de uso para crear usuario"""')
    create_file("src/modules/users/application/useCases/LoginUser.py", '"""Caso de uso para login de usuario"""')
    create_file("src/modules/users/application/useCases/UpdateProfile.py", '"""Caso de uso para actualizar perfil"""')
    create_file("src/modules/users/application/useCases/VerifyEmail.py", '"""Caso de uso para verificar email"""')
    create_file("src/modules/users/application/useCases/ResendVerification.py", '"""Caso de uso para reenviar verificación"""')
    create_file("src/modules/users/application/useCases/RequestPasswordReset.py", '"""Caso de uso para solicitar reset de contraseña"""')
    create_file("src/modules/users/application/useCases/ResetPassword.py", '"""Caso de uso para resetear contraseña"""')
    
    # Infrastructure layer
    create_file("src/modules/users/infrastructure/controllers/UserController.py", '"""Controlador para usuarios"""')
    create_file("src/modules/users/infrastructure/repositories/UserMongoRepository.py", '"""Implementación concreta del repositorio para MongoDB"""')
    create_file("src/modules/users/infrastructure/routes/UserRoutes.py", '"""Rutas para el módulo de usuarios"""')
    
    # Shared components
    create_file("src/shared/database/Connection.py", '"""Conexión a base de datos"""')
    create_file("src/shared/services/AuthService.py", '"""Servicio de autenticación JWT"""')
    create_file("src/shared/services/EmailService.py", '"""Servicio de emails (SendGrid)"""')
    create_file("src/shared/services/UploadService.py", '"""Servicio de subida de archivos"""')
    create_file("src/shared/middleware/AuthMiddleware.py", '"""Middleware de autenticación"""')
    
    # Exceptions
    create_file("src/shared/exceptions/UserExceptions.py", '"""Excepciones relacionadas con usuarios"""')
    create_file("src/shared/exceptions/AuthExceptions.py", '"""Excepciones relacionadas con autenticación"""')
    create_file("src/shared/exceptions/EmailExceptions.py", '"""Excepciones relacionadas con emails"""')
    create_file("src/shared/exceptions/UploadExceptions.py", '"""Excepciones relacionadas con subida de archivos"""')
    
    # Email templates
    create_file("src/shared/templates/emails/welcome.html", '<!-- Template para email de bienvenida -->')
    create_file("src/shared/templates/emails/verification.html", '<!-- Template para email de verificación -->')
    create_file("src/shared/templates/emails/password_reset.html", '<!-- Template para email de reset de contraseña -->')
    create_file("src/shared/templates/emails/password_changed.html", '<!-- Template para email de contraseña cambiada -->')
    create_file("src/shared/templates/emails/account_deleted.html", '<!-- Template para email de cuenta eliminada -->')
    
    # Shared DTOs, controllers and routes
    create_file("src/shared/dtos/UploadDTOs.py", '"""DTOs para subida de archivos"""')
    create_file("src/shared/controllers/UploadController.py", '"""Controlador para subida de archivos"""')
    create_file("src/shared/routes/UploadRoutes.py", '"""Rutas para subida de archivos"""')

if __name__ == "__main__":
    create_project_structure()
    print("Estructura de proyecto creada exitosamente!")