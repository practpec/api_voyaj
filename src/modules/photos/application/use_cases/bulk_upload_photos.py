# src/modules/photos/application/use_cases/bulk_upload_photos.py
from typing import Dict, Any, List
from fastapi import UploadFile
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from ...domain.photo_service import PhotoService
from ...domain.Photo import Photo
from ..dtos.photo_dto import BulkUploadDTO
from shared.services.UploadService import UploadService
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException,
    ValidationException
)

class BulkUploadPhotosUseCase:
    """Caso de uso para subida masiva de fotos"""

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
        files: List[UploadFile], 
        dto: BulkUploadDTO, 
        user_id: str
    ) -> Dict[str, Any]:
        """Ejecutar subida masiva de fotos"""
        
        # Validar que usuario puede acceder al viaje
        if not await self.photo_service.validate_user_can_access_trip_photos(dto.trip_id, user_id):
            raise UnauthorizedException("No tienes permisos para subir fotos a este viaje")

        # Validar usuario existe
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundException("Usuario no encontrado")

        # Validar que no exceda el límite de archivos
        if len(files) > 10:
            raise ValidationException("Máximo 10 fotos por subida masiva")

        successful_uploads = []
        failed_uploads = []

        for i, file in enumerate(files):
            try:
                # Subir archivo a Cloudinary usando el método existente
                upload_result = await self.upload_service.upload_trip_photo(
                    file, dto.trip_id, user_id
                )

                # Crear entidad foto
                photo = Photo(
                    trip_id=dto.trip_id,
                    user_id=user_id,
                    day_id=dto.day_id,
                    title=f"{file.filename}" if file.filename else f"Foto {i+1}",
                    tags=dto.default_tags or [],
                    url=upload_result["url"],
                    public_id=upload_result["public_id"]
                )

                # Guardar en base de datos
                created_photo = await self.photo_repository.create(photo)
                
                successful_uploads.append({
                    "file_name": file.filename,
                    "photo_id": created_photo.id,
                    "url": created_photo.url
                })

            except Exception as e:
                failed_uploads.append({
                    "file_name": file.filename,
                    "error": str(e)
                })

        return {
            "success": True,
            "message": f"{len(successful_uploads)} fotos subidas exitosamente",
            "data": {
                "successful_uploads": successful_uploads,
                "failed_uploads": failed_uploads,
                "total_attempted": len(files),
                "total_successful": len(successful_uploads),
                "total_failed": len(failed_uploads)
            }
        }