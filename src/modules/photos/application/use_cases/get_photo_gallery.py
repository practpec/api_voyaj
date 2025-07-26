# src/modules/photos/application/use_cases/get_photo_gallery.py
from typing import Dict, Any
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from ...domain.photo_service import PhotoService
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException
)

class GetPhotoGalleryUseCase:
    """Caso de uso para obtener galería organizada de fotos"""

    def __init__(
        self,
        photo_repository: IPhotoRepository,
        trip_member_repository: ITripMemberRepository,
        photo_service: PhotoService
    ):
        self.photo_repository = photo_repository
        self.trip_member_repository = trip_member_repository
        self.photo_service = photo_service

    async def execute(
        self, 
        trip_id: str, 
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Ejecutar obtención de galería"""
        
        # Validar que usuario puede acceder al viaje
        if not await self.photo_service.validate_user_can_access_trip_photos(trip_id, user_id):
            raise UnauthorizedException("No tienes permisos para ver la galería de este viaje")

        # Obtener fotos del viaje
        photos = await self.photo_repository.get_by_trip_id(trip_id, limit, offset)
        
        # Obtener estadísticas del viaje
        trip_summary = await self.photo_service.get_trip_photo_summary(trip_id)
        
        # Obtener fotos más populares
        most_liked = await self.photo_repository.get_most_liked_photos(trip_id, 5)

        # Organizar fotos con contexto de usuario
        gallery_photos = []
        for photo in photos:
            gallery_photos.append({
                "id": photo.id,
                "title": photo.title,
                "url": photo.url,
                "thumbnail_url": photo.thumbnail_url,
                "day_id": photo.day_id,
                "likes_count": photo.get_likes_count(),
                "is_liked": photo.has_like_from(user_id),
                "uploaded_at": photo.uploaded_at,
                "user_id": photo.user_id
            })

        # Formatear fotos más populares
        popular_photos = []
        for photo in most_liked:
            popular_photos.append({
                "id": photo.id,
                "title": photo.title,
                "url": photo.url,
                "thumbnail_url": photo.thumbnail_url,
                "likes_count": photo.get_likes_count(),
                "is_liked": photo.has_like_from(user_id)
            })

        return {
            "success": True,
            "data": {
                "gallery": {
                    "photos": gallery_photos,
                    "total": trip_summary["total_photos"],
                    "page": offset // limit + 1,
                    "has_more": offset + limit < trip_summary["total_photos"]
                },
                "stats": {
                    "total_photos": trip_summary["total_photos"],
                    "photos_by_day": trip_summary["photos_by_day"],
                    "most_liked": popular_photos
                }
            }
        }