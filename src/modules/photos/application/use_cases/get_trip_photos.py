# src/modules/photos/application/use_cases/get_trip_photos.py
from typing import Dict, Any, Optional
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from ...domain.photo_service import PhotoService
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException
)

class GetTripPhotosUseCase:
    """Caso de uso para obtener fotos de un viaje"""

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
        trip_id: str, 
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        day_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Ejecutar obtención de fotos del viaje"""
        
        # Validar que usuario puede acceder al viaje
        if not await self.photo_service.validate_user_can_access_trip_photos(trip_id, user_id):
            raise UnauthorizedException("No tienes permisos para ver las fotos de este viaje")

        # Obtener fotos
        photos = await self.photo_repository.get_by_trip_id(trip_id, limit, offset, day_id)
        
        # Obtener total para paginación
        total = await self.photo_repository.count_by_trip_id(trip_id)

        # Agregar contexto de usuario para cada foto
        photos_with_context = []
        for photo in photos:
            photos_with_context.append({
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
                "likes_count": photo.get_likes_count(),
                "is_liked": photo.has_like_from(user_id),
                "uploaded_at": photo.uploaded_at
            })

        return {
            "success": True,
            "data": {
                "photos": photos_with_context,
                "pagination": {
                    "total": total,
                    "limit": limit,
                    "offset": offset,
                    "has_more": offset + limit < total
                }
            }
        }