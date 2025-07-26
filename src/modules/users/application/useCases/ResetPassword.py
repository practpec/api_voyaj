from ...domain.interfaces.IUserRepository import IUserRepository
from shared.services.EmailService import EmailService
from shared.exceptions.UserExceptions import UserNotFoundException
from shared.exceptions.AuthExceptions import InvalidCredentialsException

class ResetPasswordUseCase:
    def __init__(self, user_repository: IUserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    async def execute(self, email: str, code: str, new_password: str) -> None:
        """Resetear contraseña con código de verificación"""
        # Buscar usuario por email
        user = await self.user_repository.find_by_email(email)
        if not user or user.eliminado:
            raise UserNotFoundException("Usuario no encontrado")

        # Resetear contraseña con código
        if not user.reset_password_with_code(code, new_password):
            raise InvalidCredentialsException("Código de recuperación inválido o expirado")

        # Guardar cambios
        await self.user_repository.update(user)

        # Enviar confirmación por email
        await self.email_service.send_password_changed_email(
            user.correo_electronico,
            user.nombre
        )