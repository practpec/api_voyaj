# src/modules/photos/infrastructure/controllers/photo_controller.py
from fastapi import HTTPException, status, UploadFile
from typing import Dict, Any, Optional
from ...application.use_cases.create_photo import CreatePhotoUseCase
from ...application.use_cases.get_photo import GetPhotoUseCase
from ...application.use_cases.get_trip_photos import GetTripPhotosUseCase
from ...application.use_cases.update_photo import UpdatePhotoUseCase
from ...application.use_cases.delete_photo import DeletePhotoUseCase
from ...application.use_cases.like_photo import LikePhotoUseCase
from ...application.use_cases.get_photo_gallery import GetPhotoGalleryUseCase
from ...application.dtos.photo_dto import CreatePhotoDTO, UpdatePhotoDTO
from shared.exceptions.common_exceptions import (
    NotFoundException, 
    UnauthorizedException, 
    ValidationException
)

class PhotoController:
    """Controlador para gestión de fotos"""

    def __init__(
        self,
        create_photo_use_case: CreatePhotoUseCase,
        get_photo_use_case: GetPhotoUseCase,
        get_trip_photos_use_case: GetTripPhotosUseCase,
        update_photo_use_case: UpdatePhotoUseCase,
        delete_photo_use_case: DeletePhotoUseCase,
        like_photo_use_case: LikePhotoUseCase,
        get_photo_gallery_use_case: GetPhotoGalleryUseCase
    ):
        self.create_photo_use_case = create_photo_use_case
        self.get_photo_use_case = get_photo_use_case
        self.get_trip_photos_use_case = get_trip_photos_use_case
        self.update_photo_use_case = update_photo_use_case
        self.delete_photo_use_case = delete_photo_use_case
        self.like_photo_use_case = like_photo_use_case
        self.get_photo_gallery_use_case = get_photo_gallery_use_case

    async def create_photo(
        self, 
        file: UploadFile, 
        dto: CreatePhotoDTO, 
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crear nueva foto"""
        try:
            return await self.create_photo_use_case.execute(file, dto, current_user["sub"])
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UnauthorizedException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValidationException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def get_photo(self, photo_id: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener foto por ID"""
        try:
            return await self.get_photo_use_case.execute(photo_id, current_user["sub"])
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UnauthorizedException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    async def get_trip_photos(
        self, 
        trip_id: str, 
        current_user: Dict[str, Any],
        limit: int = 20,
        offset: int = 0,
        day_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtener fotos de un viaje"""
        try:
            return await self.get_trip_photos_use_case.execute(
                trip_id, current_user["sub"], limit, offset, day_id
            )
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UnauthorizedException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    async def update_photo(
        self, 
        photo_id: str, 
        dto: UpdatePhotoDTO, 
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualizar información de foto"""
        try:
            return await self.update_photo_use_case.execute(photo_id, dto, current_user["sub"])
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UnauthorizedException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValidationException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    async def delete_photo(self, photo_id: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Eliminar foto"""
        try:
            return await self.delete_photo_use_case.execute(photo_id, current_user["sub"])
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UnauthorizedException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    async def like_photo(self, photo_id: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Dar/quitar like a foto"""
        try:
            return await self.like_photo_use_case.execute(photo_id, current_user["sub"])
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UnauthorizedException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    async def get_photo_gallery(
        self, 
        trip_id: str, 
        current_user: Dict[str, Any],
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Obtener galería de fotos del viaje"""
        try:
            return await self.get_photo_gallery_use_case.execute(
                trip_id, current_user["sub"], limit, offset
            )
        except NotFoundException as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UnauthorizedException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))