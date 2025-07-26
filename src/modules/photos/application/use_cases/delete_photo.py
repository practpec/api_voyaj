# src/modules/photos/application/use_cases/delete_photo.py
from typing import Dict, Any
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from ...domain.photo_service import PhotoService
from shared.services.UploadService import UploadService
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException
)

class DeletePhotoUseCase:
    """Caso de uso para eliminar foto"""

    def __init__(
        self,
        photo_repository: IPhotoRepository,
        photo_service: PhotoService,
        upload_service: UploadService
    ):
        self.photo_repository = photo_repository
        self.photo_service = photo_service
        self.upload_service = upload_service

    async def execute(self, photo_id: str, user_id: str) -> Dict[str, Any]:
        """Ejecutar eliminación de foto"""
        
        # Obtener foto existente
        photo = await self.photo_repository.get_by_id(photo_id)
        if not photo:
            raise NotFoundException("Foto no encontrada")

        # Validar que usuario puede modificar la foto
        if not await self.photo_service.validate_user_can_modify_photo(photo, user_id):
            raise UnauthorizedException("No tienes permisos para eliminar esta foto")

        try:
            # Eliminar archivo de Cloudinary
            await self.upload_service.delete_file(photo.public_id, "image")
            
            # Eliminar registro de base de datos
            deleted = await self.photo_repository.delete(photo_id)
            
            if not deleted:
                raise Exception("Error al eliminar foto de la base de datos")

            return {
                "success": True,
                "message": "Foto eliminada exitosamente"
            }

        except Exception as e:
            raise Exception(f"Error al eliminar foto: {str(e)}")