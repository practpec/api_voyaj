from ...domain.interfaces.IUserRepository import IUserRepository
from shared.services.EmailService import EmailService

class RequestPasswordResetUseCase:
    def __init__(self, user_repository: IUserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    async def execute(self, email: str) -> None:
        """Solicitar reset de contraseña"""
        # Buscar usuario por email
        user = await self.user_repository.find_by_email(email)
        if not user or user.eliminado or not user.esta_activo:
            # Por seguridad, siempre responder con éxito
            return

        # Generar código de recuperación
        reset_code = user.generate_password_reset_code()
        await self.user_repository.update(user)

        # Enviar email con código
        await self.email_service.send_password_reset_email(
            user.correo_electronico,
            user.nombre,
            reset_code
        )