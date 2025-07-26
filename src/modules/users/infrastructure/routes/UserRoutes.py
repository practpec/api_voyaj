from fastapi import APIRouter, Depends, UploadFile, File, Query
from ..controllers.UserController import UserController
from ...application.dtos.UserDTOs import (
    CreateUserDTO, 
    LoginDTO, 
    UpdateProfileDTO,
    VerifyEmailDTO,
    ResendVerificationDTO,
    RequestPasswordResetDTO,
    ResetPasswordDTO
)
from shared.services.AuthService import AuthService
from shared.services.EmailService import EmailService
from shared.services.UploadService import UploadService
from shared.middleware.AuthMiddleware import get_current_user
from ..repositories.UserMongoRepository import UserMongoRepository

router = APIRouter()

# Dependency injection
def get_user_repository():
    return UserMongoRepository()

def get_auth_service():
    return AuthService()

def get_email_service():
    return EmailService()

def get_upload_service():
    return UploadService()

def get_user_controller(
    user_repository: UserMongoRepository = Depends(get_user_repository),
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailService = Depends(get_email_service)
):
    return UserController(user_repository, auth_service, email_service)

# ============================================================================
# ENDPOINTS PÚBLICOS (sin autenticación)
# ============================================================================

@router.post("/register")
async def register(
    user_data: CreateUserDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Registrar un nuevo usuario en el sistema.
    
    - **correo_electronico**: Email único del usuario
    - **nombre**: Nombre completo del usuario  
    - **contrasena**: Contraseña (mínimo 8 caracteres)
    
    Se enviará un email de verificación automáticamente.
    """
    return await controller.register(user_data)

@router.post("/login")
async def login(
    login_data: LoginDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Iniciar sesión con email y contraseña.
    
    - **correo_electronico**: Email del usuario
    - **contrasena**: Contraseña del usuario
    
    Retorna access_token y refresh_token.
    """
    return await controller.login(login_data)

@router.post("/verify-email")
async def verify_email(
    verify_data: VerifyEmailDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Verificar email con código de 6 dígitos.
    
    - **correo_electronico**: Email del usuario
    - **codigo**: Código de verificación de 6 dígitos
    
    El código expira en 24 horas.
    """
    return await controller.verify_email(verify_data)

@router.post("/resend-verification")
async def resend_verification(
    resend_data: ResendVerificationDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Reenviar código de verificación de email.
    
    - **correo_electronico**: Email del usuario
    
    Solo se envía si el email no está verificado.
    """
    return await controller.resend_verification(resend_data)

@router.post("/forgot-password")
async def request_password_reset(
    reset_request: RequestPasswordResetDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Solicitar código de recuperación de contraseña.
    
    - **correo_electronico**: Email del usuario
    
    Se enviará un código de 6 dígitos que expira en 10 minutos.
    """
    return await controller.request_password_reset(reset_request)

@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Restablecer contraseña con código de recuperación.
    
    - **correo_electronico**: Email del usuario
    - **codigo**: Código de recuperación de 6 dígitos
    - **nueva_contrasena**: Nueva contraseña (mínimo 8 caracteres)
    
    El código expira en 10 minutos por seguridad.
    """
    return await controller.reset_password(reset_data)

# ============================================================================
# ENDPOINTS PROTEGIDOS (requieren autenticación)
# ============================================================================

@router.get("/profile")
async def get_profile(
    controller: UserController = Depends(get_user_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener el perfil completo del usuario autenticado.
    
    Requiere token de autenticación válido en header:
    Authorization: Bearer <access_token>
    """
    return await controller.get_profile(current_user)

@router.put("/profile")
async def update_profile(
    profile_data: UpdateProfileDTO,
    controller: UserController = Depends(get_user_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar información del perfil del usuario.
    
    Campos opcionales:
    - **nombre**: Nuevo nombre
    - **url_foto_perfil**: Nueva URL de foto de perfil
    - **telefono**: Número de teléfono
    - **pais**: País de residencia
    - **ciudad**: Ciudad de residencia
    - **fecha_nacimiento**: Fecha de nacimiento
    - **biografia**: Biografía personal (máximo 500 caracteres)
    """
    return await controller.update_profile(profile_data, current_user)

@router.post("/profile/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir nueva foto de perfil.
    
    - **file**: Archivo de imagen (JPG, PNG, WebP, GIF)
    - **Tamaño máximo**: 5MB
    - **Optimización**: Se redimensiona automáticamente a 400x400px
    
    La imagen anterior se reemplaza automáticamente.
    """
    from shared.controllers.UploadController import UploadController
    upload_controller = UploadController()
    return await upload_controller.upload_profile_picture(file, current_user)

@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=2, description="Término de búsqueda"),
    limit: int = Query(10, ge=1, le=50, description="Número de resultados"),
    offset: int = Query(0, ge=0, description="Número de resultados a omitir"),
    controller: UserController = Depends(get_user_controller)
):
    """
    Buscar usuarios por nombre o email.
    
    - **query**: Término de búsqueda (mínimo 2 caracteres)
    - **limit**: Número máximo de resultados (1-50, por defecto 10)
    - **offset**: Número de resultados a omitir para paginación
    
    Ejemplo: `/api/users/search?query=juan&limit=20&offset=0`
    """
    return await controller.search_users(query, limit, offset)