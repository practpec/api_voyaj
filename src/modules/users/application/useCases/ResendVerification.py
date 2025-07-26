from ...domain.interfaces.IUserRepository import IUserRepository
from shared.services.EmailService import EmailService
from shared.exceptions.UserExceptions import UserNotFoundException

class ResendVerificationUseCase:
    def __init__(self, user_repository: IUserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    async def execute(self, email: str) -> None:
        """Reenviar código de verificación de email"""
        # Buscar usuario por email
        user = await self.user_repository.find_by_email(email)
        if not user or user.eliminado:
            # Por seguridad, no revelamos si el email existe
            return

        # Si ya está verificado, no hacer nada
        if user.email_verificado:
            return

        # Generar nuevo código
        verification_code = user.generate_email_verification_code()
        await self.user_repository.update(user)

        # Enviar email
        await self.email_service.send_verification_email(
            user.correo_electronico,
            user.nombre,
            verification_code
        )