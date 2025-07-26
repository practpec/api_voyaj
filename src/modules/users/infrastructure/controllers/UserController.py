from fastapi import HTTPException, status
from typing import List
from ...application.dtos.UserDTOs import (
    CreateUserDTO, 
    LoginDTO, 
    UpdateProfileDTO, 
    VerifyEmailDTO,
    ResendVerificationDTO,
    RequestPasswordResetDTO,
    ResetPasswordDTO,
    AuthResponseDTO, 
    AuthenticatedUserDTO,
    UserSearchResultDTO,
    SearchUsersResponseDTO
)
from ...application.useCases.CreateUser import CreateUserUseCase
from ...application.useCases.LoginUser import LoginUserUseCase
from ...application.useCases.UpdateProfile import UpdateProfileUseCase
from ...application.useCases.VerifyEmail import VerifyEmailUseCase
from ...application.useCases.ResendVerification import ResendVerificationUseCase
from ...application.useCases.RequestPasswordReset import RequestPasswordResetUseCase
from ...application.useCases.ResetPassword import ResetPasswordUseCase
from ...domain.interfaces.IUserRepository import IUserRepository
from shared.services.AuthService import AuthService
from shared.services.EmailService import EmailService
from shared.exceptions.UserExceptions import UserNotFoundException, UserAlreadyExistsException
from shared.exceptions.AuthExceptions import InvalidCredentialsException, UserNotActiveException

class UserController:
    def __init__(self, user_repository: IUserRepository, auth_service: AuthService, email_service: EmailService):
        self.user_repository = user_repository
        self.auth_service = auth_service
        self.email_service = email_service
        
        # Casos de uso
        self.create_user_use_case = CreateUserUseCase(user_repository, email_service)
        self.login_user_use_case = LoginUserUseCase(user_repository, auth_service)
        self.update_profile_use_case = UpdateProfileUseCase(user_repository)
        self.verify_email_use_case = VerifyEmailUseCase(user_repository)
        self.resend_verification_use_case = ResendVerificationUseCase(user_repository, email_service)
        self.request_password_reset_use_case = RequestPasswordResetUseCase(user_repository, email_service)
        self.reset_password_use_case = ResetPasswordUseCase(user_repository, email_service)

    async def register(self, user_data: CreateUserDTO) -> dict:
        try:
            user = await self.create_user_use_case.execute(user_data)
            return {
                "success": True,
                "message": "Usuario creado exitosamente. Revisa tu email para verificar tu cuenta.",
                "data": user
            }
        except UserAlreadyExistsException as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def login(self, login_data: LoginDTO) -> dict:
        try:
            auth_response = await self.login_user_use_case.execute(login_data)
            return {
                "success": True,
                "message": "Login exitoso",
                "data": auth_response
            }
        except (InvalidCredentialsException, UserNotActiveException) as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def verify_email(self, verify_data: VerifyEmailDTO) -> dict:
        try:
            await self.verify_email_use_case.execute(verify_data.correo_electronico, verify_data.codigo)
            return {
                "success": True,
                "message": "Email verificado exitosamente"
            }
        except (UserNotFoundException, InvalidCredentialsException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def resend_verification(self, resend_data: ResendVerificationDTO) -> dict:
        try:
            await self.resend_verification_use_case.execute(resend_data.correo_electronico)
            return {
                "success": True,
                "message": "Código de verificación enviado"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def request_password_reset(self, reset_request: RequestPasswordResetDTO) -> dict:
        try:
            await self.request_password_reset_use_case.execute(reset_request.correo_electronico)
            return {
                "success": True,
                "message": "Si el email existe, se ha enviado un código de recuperación"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def reset_password(self, reset_data: ResetPasswordDTO) -> dict:
        try:
            await self.reset_password_use_case.execute(
                reset_data.correo_electronico,
                reset_data.codigo,
                reset_data.nueva_contrasena
            )
            return {
                "success": True,
                "message": "Contraseña restablecida exitosamente"
            }
        except (UserNotFoundException, InvalidCredentialsException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def get_profile(self, current_user: dict) -> dict:
        try:
            user = await self.user_repository.find_by_id(current_user["sub"])
            if not user or user.eliminado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            user_dto = AuthenticatedUserDTO(
                id=user.id,
                correo_electronico=user.correo_electronico,
                nombre=user.nombre,
                url_foto_perfil=user.url_foto_perfil,
                telefono=user.telefono,
                pais=user.pais,
                ciudad=user.ciudad,
                fecha_nacimiento=user.fecha_nacimiento,
                biografia=user.biografia,
                preferencias=user.preferencias,
                esta_activo=user.esta_activo,
                email_verificado=user.email_verificado,
                plan=user.plan,
                creado_en=user.creado_en,
                ultimo_acceso=user.ultimo_acceso
            )
            
            return {
                "success": True,
                "message": "Perfil obtenido exitosamente",
                "data": user_dto
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def update_profile(self, profile_data: UpdateProfileDTO, current_user: dict) -> dict:
        try:
            updated_user = await self.update_profile_use_case.execute(
                current_user["sub"], 
                profile_data
            )
            return {
                "success": True,
                "message": "Perfil actualizado exitosamente",
                "data": updated_user
            }
        except UserNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def search_users(self, query: str, limit: int = 10, offset: int = 0) -> dict:
        try:
            users = await self.user_repository.search_users(query, limit, offset)
            total = await self.user_repository.count_users()
            
            user_results = [
                UserSearchResultDTO(
                    id=user.id,
                    correo_electronico=user.correo_electronico,
                    nombre=user.nombre,
                    url_foto_perfil=user.url_foto_perfil
                )
                for user in users
            ]
            
            response = SearchUsersResponseDTO(
                users=user_results,
                total=total,
                page=(offset // limit) + 1,
                limit=limit
            )
            
            return {
                "success": True,
                "message": "Búsqueda completada",
                "data": response
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def verify_email(self, verify_data: VerifyEmailDTO) -> dict:
        try:
            await self.verify_email_use_case.execute(verify_data.correo_electronico, verify_data.codigo)
            return {
                "success": True,
                "message": "Email verificado exitosamente"
            }
        except (UserNotFoundException, InvalidCredentialsException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def resend_verification(self, resend_data: ResendVerificationDTO) -> dict:
        try:
            await self.resend_verification_use_case.execute(resend_data.correo_electronico)
            return {
                "success": True,
                "message": "Código de verificación enviado"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def request_password_reset(self, reset_request: RequestPasswordResetDTO) -> dict:
        try:
            await self.request_password_reset_use_case.execute(reset_request.correo_electronico)
            return {
                "success": True,
                "message": "Si el email existe, se ha enviado un código de recuperación"
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def reset_password(self, reset_data: ResetPasswordDTO) -> dict:
        try:
            await self.reset_password_use_case.execute(
                reset_data.correo_electronico,
                reset_data.codigo,
                reset_data.nueva_contrasena
            )
            return {
                "success": True,
                "message": "Contraseña restablecida exitosamente"
            }
        except (UserNotFoundException, InvalidCredentialsException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def get_profile(self, current_user: dict) -> dict:
        try:
            user = await self.user_repository.find_by_id(current_user["sub"])
            if not user or user.eliminado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado"
                )
            
            user_dto = AuthenticatedUserDTO(
                id=user.id,
                correo_electronico=user.correo_electronico,
                nombre=user.nombre,
                url_foto_perfil=user.url_foto_perfil,
                telefono=user.telefono,
                pais=user.pais,
                ciudad=user.ciudad,
                fecha_nacimiento=user.fecha_nacimiento,
                biografia=user.biografia,
                preferencias=user.preferencias,
                esta_activo=user.esta_activo,
                email_verificado=user.email_verificado,
                plan=user.plan,
                creado_en=user.creado_en,
                ultimo_acceso=user.ultimo_acceso
            )
            
            return {
                "success": True,
                "message": "Perfil obtenido exitosamente",
                "data": user_dto
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def update_profile(self, profile_data: UpdateProfileDTO, current_user: dict) -> dict:
        try:
            updated_user = await self.update_profile_use_case.execute(
                current_user["sub"], 
                profile_data
            )
            return {
                "success": True,
                "message": "Perfil actualizado exitosamente",
                "data": updated_user
            }
        except UserNotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )

    async def search_users(self, query: str, limit: int = 10, offset: int = 0) -> dict:
        try:
            users = await self.user_repository.search_users(query, limit, offset)
            total = await self.user_repository.count_users()
            
            user_results = [
                UserSearchResultDTO(
                    id=user.id,
                    correo_electronico=user.correo_electronico,
                    nombre=user.nombre,
                    url_foto_perfil=user.url_foto_perfil
                )
                for user in users
            ]
            
            response = SearchUsersResponseDTO(
                users=user_results,
                total=total,
                page=(offset // limit) + 1,
                limit=limit
            )
            
            return {
                "success": True,
                "message": "Búsqueda completada",
                "data": response
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )