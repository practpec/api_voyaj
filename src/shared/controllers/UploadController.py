# src/shared/controllers/UploadController.py
from fastapi import HTTPException, UploadFile, status
from typing import List
from ..services.ServiceFactory import ServiceFactory
from ..repositories.RepositoryFactory import RepositoryFactory
from ..dtos.UploadDTOs import (
    UploadResponseDTO, 
    MultipleUploadResponseDTO, 
    ProfilePictureUploadDTO,
    TripPhotoUploadDTO,
    DocumentUploadDTO
)
from ..exceptions.UploadExceptions import (
    FileTooLargeException, 
    InvalidFileTypeException, 
    CloudinaryException
)
from ..utils.response_utils import ResponseUtils

class UploadController:
    def __init__(self):
        self.upload_service = ServiceFactory.get_upload_service()
        self.user_repository = RepositoryFactory.get_user_repository()

    async def upload_profile_picture(self, file: UploadFile, current_user: dict) -> dict:
        """Subir foto de perfil y actualizar BD automáticamente"""
        try:
            user_id = current_user["sub"]
            
            # 1. Buscar usuario actual para eliminar imagen anterior
            user = await self.user_repository.find_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail="Usuario no encontrado"
                )
            
            # 2. Eliminar imagen anterior si existe
            if user.url_foto_perfil:
                try:
                    old_public_id = self.upload_service.extract_public_id_from_url(user.url_foto_perfil)
                    if old_public_id:
                        await self.upload_service.delete_file(old_public_id)
                except Exception:
                    # Si falla la eliminación, continuar
                    pass
            
            # 3. Subir nueva imagen
            upload_result = await self.upload_service.upload_profile_picture(file, user_id)
            
            # 4. Actualizar URL en la BD
            user.update_profile(url_foto_perfil=upload_result["url"])
            await self.user_repository.update(user)
            
            response_dto = ProfilePictureUploadDTO(
                url=upload_result["url"],
                public_id=upload_result["public_id"]
            )
            
            return ResponseUtils.success(
                data=response_dto,
                message="Foto de perfil actualizada exitosamente"
            ).__dict__
            
        except (FileTooLargeException, InvalidFileTypeException) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except CloudinaryException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error interno del servidor: {str(e)}"
            )

    async def upload_trip_photos(self, trip_id: str, files: List[UploadFile], current_user: dict) -> dict:
        """Subir múltiples fotos de viaje"""
        try:
            user_id = current_user["sub"]
            result = await self.upload_service.upload_trip_photos(trip_id, files, user_id)
            
            response_dto = MultipleUploadResponseDTO(
                uploaded=result["uploaded"],
                failed=result["failed"],
                total_uploaded=result["total_uploaded"],
                total_failed=result["total_failed"]
            )
            
            return ResponseUtils.success(
                data=response_dto,
                message=f"Proceso completado: {result['total_uploaded']} fotos subidas, {result['total_failed']} fallidas"
            ).__dict__
            
        except (FileTooLargeException, InvalidFileTypeException) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except CloudinaryException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def upload_document(self, folder: str, file: UploadFile, current_user: dict) -> dict:
        """Subir documento a carpeta específica"""
        try:
            user_id = current_user["sub"]
            result = await self.upload_service.upload_document(folder, file, user_id)
            
            response_dto = DocumentUploadDTO(
                url=result["url"],
                public_id=result["public_id"],
                filename=result["filename"]
            )
            
            return ResponseUtils.success(
                data=response_dto,
                message="Documento subido exitosamente"
            ).__dict__
            
        except (FileTooLargeException, InvalidFileTypeException) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except CloudinaryException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    async def delete_file(self, public_id: str, resource_type: str, current_user: dict) -> dict:
        """Eliminar archivo de Cloudinary"""
        try:
            success = await self.upload_service.delete_file(public_id, resource_type)
            
            if success:
                return ResponseUtils.success(
                    data={"public_id": public_id, "deleted": True},
                    message="Archivo eliminado exitosamente"
                ).__dict__
            else:
                raise CloudinaryException("No se pudo eliminar el archivo")
                
        except CloudinaryException as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))