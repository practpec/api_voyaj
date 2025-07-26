# src/modules/photos/application/use_cases/create_photo.py
from typing import Dict, Any
from fastapi import UploadFile
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from ...domain.photo_service import PhotoService
from ...domain.Photo import Photo
from ..dtos.photo_dto import CreatePhotoDTO
from shared.services.UploadService import UploadService
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException,
    ValidationException
)

class CreatePhotoUseCase:
    """Caso de uso para crear nueva foto"""

    def __init__(
        self,
        photo_repository: IPhotoRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        photo_service: PhotoService,
        upload_service: UploadService
    ):
        self.photo_repository = photo_repository
        self.trip_member_repository = trip_member_repository
        self.user_repository = user_repository
        self.photo_service = photo_service
        self.upload_service = upload_service

    async def execute(
        self, 
        file: UploadFile, 
        dto: CreatePhotoDTO, 
        user_id: str
    ) -> Dict[str, Any]:
        """Ejecutar creación de foto"""
        
        # Validar que usuario puede acceder al viaje
        if not await self.photo_service.validate_user_can_access_trip_photos(dto.trip_id, user_id):
            raise UnauthorizedException("No tienes permisos para subir fotos a este viaje")

        # Validar usuario existe
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuario no encontrado")

        # Validar asociaciones
        validations = await self.photo_service.validate_photo_associations(
            dto.trip_id, 
            dto.day_id, 
            dto.diary_entry_id
        )
        
        if not all(validations.values()):
            raise ValidationException("Asociaciones de foto inválidas")

        try:
            # Subir archivo a Cloudinary
            upload_result = await self.upload_service.upload_trip_photo(
                file, dto.trip_id, user_id
            )

            # Crear entidad foto
            photo = Photo(
                trip_id=dto.trip_id,
                user_id=user_id,
                day_id=dto.day_id,
                diary_entry_id=dto.diary_entry_id,
                title=dto.title,
                description=dto.description,
                location=dto.location,
                tags=dto.tags or [],
                url=upload_result["url"],
                public_id=upload_result["public_id"]
            )

            # Guardar en base de datos
            created_photo = await self.photo_repository.create(photo)

            return {
                "success": True,
                "message": "Foto subida exitosamente",
                "data": {
                    "id": created_photo.id,
                    "url": created_photo.url,
                    "trip_id": created_photo.trip_id,
                    "title": created_photo.title,
                    "uploaded_at": created_photo.uploaded_at
                }
            }

        except Exception as e:
            raise ValidationException(f"Error al subir foto: {str(e)}")