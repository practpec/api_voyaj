from ..dtos.UserDTOs import CreateUserDTO, AuthenticatedUserDTO
from ...domain.User import User
from ...domain.interfaces.IUserRepository import IUserRepository
from shared.exceptions.UserExceptions import UserAlreadyExistsException
from shared.services.EmailService import EmailService

class CreateUserUseCase:
    def __init__(self, user_repository: IUserRepository, email_service: EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    async def execute(self, user_data: CreateUserDTO) -> AuthenticatedUserDTO:
        # Verificar si el usuario ya existe
        existing_user = await self.user_repository.find_by_email(user_data.correo_electronico)
        if existing_user:
            raise UserAlreadyExistsException("El correo electrónico ya está registrado")

        # Crear nuevo usuario
        user = User(
            correo_electronico=user_data.correo_electronico,
            nombre=user_data.nombre,
            contrasena=user_data.contrasena
        )

        # Generar código de verificación
        verification_code = user.generate_email_verification_code()

        # Guardar en base de datos
        await self.user_repository.create(user)

        # Enviar email de bienvenida con código de verificación
        await self.email_service.send_welcome_email(
            user.correo_electronico,
            user.nombre,
            verification_code
        )

        # Retornar DTO del usuario creado
        return AuthenticatedUserDTO(
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