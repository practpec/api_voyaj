# src/modules/photos/application/use_cases/get_photo.py
from typing import Dict, Any
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from ...domain.photo_service import PhotoService
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException
)

class GetPhotoUseCase:
    """Caso de uso para obtener foto por ID"""

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

    async def execute(self, photo_id: str, user_id: str) -> Dict[str, Any]:
        """Ejecutar obtención de foto"""
        
        # Obtener foto
        photo = await self.photo_repository.get_by_id(photo_id)
        if not photo:
            raise NotFoundException("Foto no encontrada")

        # Validar que usuario puede acceder al viaje
        if not await self.photo_service.validate_user_can_access_trip_photos(photo.trip_id, user_id):
            raise UnauthorizedException("No tienes permisos para ver esta foto")

        # Obtener contexto del usuario
        photo_context = await self.photo_service.get_photo_with_user_context(photo, user_id)

        return {
            "success": True,
            "data": {
                "id": photo.id,
                "trip_id": photo.trip_id,
                "user_id": photo.user_id,
                "day_id": photo.day_id,
                "diary_entry_id": photo.diary_entry_id,
                "title": photo.title,
                "description": photo.description,
                "location": photo.location,
                "tags": photo.tags,
                "url": photo.url,
                "thumbnail_url": photo.thumbnail_url,
                "public_id": photo.public_id,
                "file_size": photo.file_size,
                "width": photo.width,
                "height": photo.height,
                "taken_at": photo.taken_at,
                "likes_count": photo.get_likes_count(),
                "is_liked": photo_context["is_liked"],
                "can_modify": photo_context["can_modify"],
                "uploaded_at": photo.uploaded_at,
                "updated_at": photo.updated_at
            }
        }