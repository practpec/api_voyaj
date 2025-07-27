# src/modules/users/infrastructure/routes/UserRoutes.py
from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException, status
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
from shared.middleware.AuthMiddleware import get_current_user, get_user_from_request
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.controllers.UploadController import UploadController

router = APIRouter()

def get_user_controller():
    return UserController(
        user_repository=RepositoryFactory.get_user_repository(),
        auth_service=ServiceFactory.get_auth_service(),
        email_service=ServiceFactory.get_email_service()
    )

def get_upload_controller():
    return UploadController()

# ===============================================
# ENDPOINTS PÚBLICOS (SIN AUTENTICACIÓN)
# ===============================================

@router.post("/register", summary="Registrar nuevo usuario")
async def register(
    user_data: CreateUserDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Registrar un nuevo usuario en el sistema.
    
    - **correo_electronico**: Email único del usuario
    - **nombre**: Nombre completo del usuario  
    - **contrasena**: Contraseña (mínimo 8 caracteres)
    
    Envía automáticamente un email de verificación.
    """
    return await controller.register(user_data)

@router.post("/login", summary="Iniciar sesión")
async def login(
    login_data: LoginDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Autenticar usuario y obtener tokens de acceso.
    
    - **correo_electronico**: Email del usuario
    - **contrasena**: Contraseña del usuario
    
    Retorna access_token y refresh_token para autenticación.
    """
    return await controller.login(login_data)

@router.post("/verify-email", summary="Verificar email")
async def verify_email(
    verify_data: VerifyEmailDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Verificar dirección de correo electrónico con código de 6 dígitos.
    
    - **correo_electronico**: Email a verificar
    - **codigo**: Código de 6 dígitos enviado por email
    """
    return await controller.verify_email(verify_data)

@router.post("/resend-verification", summary="Reenviar código de verificación")
async def resend_verification(
    resend_data: ResendVerificationDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Reenviar código de verificación de email.
    
    - **correo_electronico**: Email al que reenviar el código
    """
    return await controller.resend_verification(resend_data)

@router.post("/forgot-password", summary="Solicitar recuperación de contraseña")
async def request_password_reset(
    reset_request: RequestPasswordResetDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Solicitar código para restablecer contraseña.
    
    - **correo_electronico**: Email de la cuenta a recuperar
    
    Envía un código de recuperación por email que expira en 1 hora.
    """
    return await controller.request_password_reset(reset_request)

@router.post("/reset-password", summary="Restablecer contraseña")
async def reset_password(
    reset_data: ResetPasswordDTO,
    controller: UserController = Depends(get_user_controller)
):
    """
    Restablecer contraseña usando código de recuperación.
    
    - **correo_electronico**: Email de la cuenta
    - **codigo**: Código de recuperación de 8 dígitos
    - **nueva_contrasena**: Nueva contraseña (mínimo 8 caracteres)
    """
    return await controller.reset_password(reset_data)

# ===============================================
# ENDPOINTS PROTEGIDOS (REQUIEREN AUTENTICACIÓN)
# ===============================================

@router.get("/profile", summary="Obtener perfil del usuario actual")
async def get_profile(
    controller: UserController = Depends(get_user_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtener perfil completo del usuario autenticado.
    
    **Requiere**: Token de autorización válido en header Authorization: Bearer <token>
    
    Retorna toda la información del perfil del usuario actual.
    """
    print(f"[DEBUG] get_profile - Usuario actual: {current_user}")
    return await controller.get_profile(current_user)

@router.put("/profile", summary="Actualizar perfil")
async def update_profile(
    profile_data: UpdateProfileDTO,
    controller: UserController = Depends(get_user_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Actualizar información del perfil del usuario.
    
    **Requiere**: Token de autorización válido
    
    Permite actualizar nombre, biografía, ubicación, etc.
    """
    return await controller.update_profile(profile_data, current_user)

@router.post("/profile/picture", summary="Subir foto de perfil")
async def upload_profile_picture(
    file: UploadFile = File(...),
    upload_controller: UploadController = Depends(get_upload_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir o actualizar foto de perfil.
    
    **Requiere**: Token de autorización válido
    
    - **file**: Archivo de imagen (JPG, PNG, WebP, GIF)
    - **Tamaño máximo**: 5MB
    - **Resolución**: Se redimensiona automáticamente
    """
    return await upload_controller.upload_profile_picture(file, current_user)

@router.get("/search", summary="Buscar usuarios")
async def search_users(
    query: str = Query(..., min_length=2, description="Término de búsqueda"),
    limit: int = Query(10, ge=1, le=50, description="Cantidad de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    controller: UserController = Depends(get_user_controller)
):
    """
    Buscar usuarios por nombre o email.
    
    - **query**: Término de búsqueda (mínimo 2 caracteres)
    - **limit**: Número de resultados (1-50)
    - **offset**: Offset para paginación
    """
    return await controller.search_users(query, limit, offset)

# ===============================================
# ENDPOINT DE DEBUG (SOLO DESARROLLO)
# ===============================================

@router.get("/debug/token", summary="Debug - Verificar token actual")
async def debug_token(current_user: dict = Depends(get_current_user)):
    """
    **SOLO PARA DESARROLLO**: Verificar información del token actual.
    
    Muestra el payload decodificado del token para debugging.
    """
    return {
        "success": True,
        "message": "Token válido",
        "payload": current_user,
        "user_id": current_user.get("sub"),
        "token_type": current_user.get("type"),
        "expires": current_user.get("exp")
    }

@router.get("/debug/headers", summary="Debug - Verificar headers")
async def debug_headers(request):
    """
    **SOLO PARA DESARROLLO**: Mostrar headers de la petición.
    """
    return {
        "success": True,
        "headers": dict(request.headers),
        "authorization": request.headers.get("Authorization", "No Authorization header")
    }