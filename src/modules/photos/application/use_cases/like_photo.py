# src/modules/photos/application/use_cases/like_photo.py
from typing import Dict, Any
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from ...domain.photo_service import PhotoService
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException
)

class LikePhotoUseCase:
    """Caso de uso para dar/quitar like a foto"""

    def __init__(
        self,
        photo_repository: IPhotoRepository,
        trip_member_repository: ITripMemberRepository,
        photo_service: PhotoService
    ):
        self.photo_repository = photo_repository
        self.trip_member_repository = trip_member_repository
        self.photo_service = photo_service

    async def execute(self, photo_id: str, user_id: str) -> Dict[str, Any]:
        """Ejecutar like/unlike de foto"""
        
        # Obtener foto existente
        photo = await self.photo_repository.get_by_id(photo_id)
        if not photo:
            raise NotFoundException("Foto no encontrada")

        # Validar que usuario puede acceder al viaje
        if not await self.photo_service.validate_user_can_access_trip_photos(photo.trip_id, user_id):
            raise UnauthorizedException("No tienes permisos para interactuar con esta foto")

        # Toggle like
        if photo.has_like_from(user_id):
            photo.remove_like(user_id)
            action = "removed"
            message = "Like eliminado"
        else:
            photo.add_like(user_id)
            action = "added"
            message = "Like agregado"

        # Guardar cambios
        updated_photo = await self.photo_repository.update(photo)

        return {
            "success": True,
            "message": message,
            "data": {
                "photo_id": updated_photo.id,
                "action": action,
                "likes_count": updated_photo.get_likes_count(),
                "is_liked": updated_photo.has_like_from(user_id)
            }
        }