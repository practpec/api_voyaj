from ..dtos.UserDTOs import UpdateProfileDTO, AuthenticatedUserDTO
from ...domain.interfaces.IUserRepository import IUserRepository
from shared.exceptions.UserExceptions import UserNotFoundException

class UpdateProfileUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def execute(self, user_id: str, profile_data: UpdateProfileDTO) -> AuthenticatedUserDTO:
        # Buscar usuario
        user = await self.user_repository.find_by_id(user_id)
        if not user or user.eliminado:
            raise UserNotFoundException("Usuario no encontrado")

        # Actualizar perfil básico
        user.update_profile(
            nombre=profile_data.nombre,
            url_foto_perfil=profile_data.url_foto_perfil
        )

        # Actualizar perfil extendido
        user.update_extended_profile(
            telefono=profile_data.telefono,
            pais=profile_data.pais,
            ciudad=profile_data.ciudad,
            fecha_nacimiento=profile_data.fecha_nacimiento,
            biografia=profile_data.biografia
        )

        # Guardar cambios
        await self.user_repository.update(user)

        # Retornar usuario actualizado
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