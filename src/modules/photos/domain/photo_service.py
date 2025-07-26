# src/modules/photos/domain/photo_service.py
from typing import List, Optional, Dict, Any
from .interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from .Photo import Photo

class PhotoService:
    """Servicio de dominio para fotos"""

    def __init__(
        self,
        photo_repository: IPhotoRepository,
        trip_member_repository: ITripMemberRepository
    ):
        self.photo_repository = photo_repository
        self.trip_member_repository = trip_member_repository

    async def validate_user_can_access_trip_photos(self, trip_id: str, user_id: str) -> bool:
        """Validar si usuario puede acceder a fotos del viaje"""
        member = await self.trip_member_repository.get_by_trip_and_user(trip_id, user_id)
        return member is not None

    async def validate_user_can_modify_photo(self, photo: Photo, user_id: str) -> bool:
        """Validar si usuario puede modificar la foto"""
        # Solo el creador de la foto puede modificarla
        return photo.user_id == user_id

    async def validate_photo_associations(
        self, 
        trip_id: str, 
        day_id: Optional[str] = None, 
        diary_entry_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validar asociaciones de la foto"""
        validations = {
            "trip_exists": True,  # Se asume que ya se validó en el use case
            "day_valid": True,
            "diary_entry_valid": True
        }

        # Validaciones adicionales podrían ir aquí
        # Por ejemplo, verificar que day_id pertenece al trip_id
        
        return validations

    async def get_photo_with_user_context(self, photo: Photo, user_id: str) -> Dict[str, Any]:
        """Obtener foto con contexto del usuario"""
        return {
            "photo": photo,
            "is_liked": photo.has_like_from(user_id),
            "can_modify": await self.validate_user_can_modify_photo(photo, user_id)
        }

    async def get_trip_photo_summary(self, trip_id: str) -> Dict[str, Any]:
        """Obtener resumen de fotos del viaje"""
        stats = await self.photo_repository.get_trip_photos_stats(trip_id)
        most_liked = await self.photo_repository.get_most_liked_photos(trip_id, 3)
        
        return {
            "total_photos": stats.get("total", 0),
            "photos_by_day": stats.get("by_day", {}),
            "most_liked_photos": most_liked,
            "recent_activity": stats.get("recent", [])
        }