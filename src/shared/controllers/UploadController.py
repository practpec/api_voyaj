from fastapi import HTTPException, UploadFile, status
from typing import List
from ..services.UploadService import UploadService
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
    UploadFailedException,
    CloudinaryException
)

class UploadController:
    def __init__(self):
        self.upload_service = UploadService()

    async def upload_profile_picture(self, file: UploadFile, current_user: dict) -> dict:
        """Subir foto de perfil de usuario"""
        try:
            result = await self.upload_service.upload_profile_picture(
                file, 
                current_user["sub"]
            )
            
            response_dto = ProfilePictureUploadDTO(
                url=result["url"],
                public_id=result["public_id"]
            )
            
            return {
                "success": True,
                "message": "Foto de perfil actualizada exitosamente",
                "data": response_dto
            }
            
        except (FileTooLargeException, InvalidFileTypeException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except CloudinaryException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def upload_trip_photos(self, trip_id: str, files: List[UploadFile], current_user: dict) -> dict:
        """Subir múltiples fotos de viaje"""
        try:
            results = await self.upload_service.upload_multiple_photos(
                files, 
                f"trips/{trip_id}/photos", 
                current_user["sub"]
            )
            
            uploaded_files = [
                TripPhotoUploadDTO(
                    url=result["url"],
                    public_id=result["public_id"],
                    original_name=result.get("original_name")
                )
                for result in results
            ]
            
            response_dto = MultipleUploadResponseDTO(
                files=uploaded_files,
                total_uploaded=len(uploaded_files),
                message=f"{len(uploaded_files)} fotos subidas exitosamente"
            )
            
            return {
                "success": True,
                "message": f"{len(uploaded_files)} fotos subidas exitosamente",
                "data": response_dto
            }
            
        except (FileTooLargeException, InvalidFileTypeException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except CloudinaryException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def upload_document(self, folder: str, file: UploadFile, current_user: dict) -> dict:
        """Subir documento"""
        try:
            result = await self.upload_service.upload_document(
                file, 
                folder, 
                current_user["sub"]
            )
            
            response_dto = DocumentUploadDTO(
                url=result["url"],
                public_id=result["public_id"],
                original_name=file.filename or "documento",
                file_type=file.content_type or "unknown"
            )
            
            return {
                "success": True,
                "message": "Documento subido exitosamente",
                "data": response_dto
            }
            
        except (FileTooLargeException, InvalidFileTypeException) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except CloudinaryException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def delete_file(self, public_id: str, resource_type: str, current_user: dict) -> dict:
        """Eliminar archivo"""
        try:
            success = await self.upload_service.delete_file(public_id, resource_type)
            
            if success:
                return {
                    "success": True,
                    "message": "Archivo eliminado exitosamente"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Archivo no encontrado o ya eliminado"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error eliminando archivo"
            )