# src/modules/photos/application/use_cases/update_photo.py
from typing import Dict, Any
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from ...domain.photo_service import PhotoService
from ..dtos.photo_dto import UpdatePhotoDTO
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException,
    ValidationException
)

class UpdatePhotoUseCase:
    """Caso de uso para actualizar información de foto"""

    def __init__(
        self,
        photo_repository: IPhotoRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        photo_service: PhotoService
    ):
        self.photo_repository = photo_repository
        self.trip_member_repository = trip_member_repository
        self.user_repository = user_repository
        self.photo_service = photo_service

    async def execute(
        self, 
        photo_id: str, 
        dto: UpdatePhotoDTO, 
        user_id: str
    ) -> Dict[str, Any]:
        """Ejecutar actualización de foto"""
        
        # Obtener foto existente
        photo = await self.photo_repository.get_by_id(photo_id)
        if not photo:
            raise NotFoundException("Foto no encontrada")

        # Validar que usuario puede modificar la foto
        if not await self.photo_service.validate_user_can_modify_photo(photo, user_id):
            raise UnauthorizedException("No tienes permisos para modificar esta foto")

        # Validar nuevas asociaciones si se proporcionan
        if dto.day_id is not None or dto.diary_entry_id is not None:
            validations = await self.photo_service.validate_photo_associations(
                photo.trip_id, 
                dto.day_id, 
                dto.diary_entry_id
            )
            
            if not all(validations.values()):
                raise ValidationException("Asociaciones de foto inválidas")

        # Actualizar información de la foto
        photo.update_info(
            title=dto.title,
            description=dto.description,
            location=dto.location,
            tags=dto.tags,
            day_id=dto.day_id,
            diary_entry_id=dto.diary_entry_id
        )

        # Guardar cambios
        updated_photo = await self.photo_repository.update(photo)

        return {
            "success": True,
            "message": "Foto actualizada exitosamente",
            "data": {
                "id": updated_photo.id,
                "title": updated_photo.title,
                "description": updated_photo.description,
                "location": updated_photo.location,
                "tags": updated_photo.tags,
                "day_id": updated_photo.day_id,
                "diary_entry_id": updated_photo.diary_entry_id,
                "updated_at": updated_photo.updated_at
            }
        }