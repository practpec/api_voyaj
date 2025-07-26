from ..dtos.UserDTOs import LoginDTO, AuthResponseDTO, AuthenticatedUserDTO
from ...domain.interfaces.IUserRepository import IUserRepository
from shared.exceptions.AuthExceptions import InvalidCredentialsException, UserNotActiveException
from shared.services.AuthService import AuthService

class LoginUserUseCase:
    def __init__(self, user_repository: IUserRepository, auth_service: AuthService):
        self.user_repository = user_repository
        self.auth_service = auth_service

    async def execute(self, login_data: LoginDTO) -> AuthResponseDTO:
        # Buscar usuario por email
        user = await self.user_repository.find_by_email(login_data.correo_electronico)
        if not user:
            raise InvalidCredentialsException("Credenciales inválidas")

        # Verificar si el usuario está activo
        if not user.esta_activo or user.eliminado:
            raise UserNotActiveException("Usuario no activo")

        # Verificar contraseña
        if not user.verify_password(login_data.contrasena):
            raise InvalidCredentialsException("Credenciales inválidas")

        # Actualizar último acceso
        user.update_last_access()
        await self.user_repository.update(user)

        # Generar tokens
        access_token = self.auth_service.create_access_token({"sub": user.id})
        refresh_token = self.auth_service.create_refresh_token({"sub": user.id})

        # Crear DTOs de respuesta
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

        return AuthResponseDTO(
            user=user_dto,
            access_token=access_token,
            refresh_token=refresh_token
        )