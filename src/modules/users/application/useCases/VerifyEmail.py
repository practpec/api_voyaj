from ...domain.interfaces.IUserRepository import IUserRepository
from shared.exceptions.UserExceptions import UserNotFoundException
from shared.exceptions.AuthExceptions import InvalidCredentialsException

class VerifyEmailUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, email: str, code: str) -> bool:
        """Verificar email con código"""
        # Buscar usuario por email
        user = await self.user_repository.find_by_email(email)
        if not user or user.eliminado:
            raise UserNotFoundException("Usuario no encontrado")

        # Verificar el código
        if not user.verify_email_code(code):
            raise InvalidCredentialsException("Código de verificación inválido o expirado")

        # Guardar cambios
        await self.user_repository.update(user)
        
        return True