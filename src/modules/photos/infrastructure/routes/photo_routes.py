from fastapi import APIRouter, Depends, Query, Path, UploadFile, File, Form
from typing import Optional
from ..controllers.photo_controller import PhotoController
from ...application.dtos.photo_dto import CreatePhotoDTO, UpdatePhotoDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory

from ...application.use_cases.create_photo import CreatePhotoUseCase
from ...application.use_cases.get_photo import GetPhotoUseCase
from ...application.use_cases.get_trip_photos import GetTripPhotosUseCase
from ...application.use_cases.update_photo import UpdatePhotoUseCase
from ...application.use_cases.delete_photo import DeletePhotoUseCase
from ...application.use_cases.like_photo import LikePhotoUseCase
from ...application.use_cases.get_photo_gallery import GetPhotoGalleryUseCase
from ...domain.photo_service import PhotoService

router = APIRouter()

def get_photo_controller():
    photo_repo = RepositoryFactory.get_photo_repository()
    trip_member_repo = RepositoryFactory.get_trip_member_repository()
    user_repo = RepositoryFactory.get_user_repository()
    upload_service = ServiceFactory.get_upload_service()
    
    photo_service = PhotoService(
        photo_repository=photo_repo,
        trip_member_repository=trip_member_repo
    )
    
    create_photo_use_case = CreatePhotoUseCase(
        photo_repository=photo_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        photo_service=photo_service,
        upload_service=upload_service
    )
    
    get_photo_use_case = GetPhotoUseCase(
        photo_repository=photo_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        photo_service=photo_service
    )
    
    get_trip_photos_use_case = GetTripPhotosUseCase(
        photo_repository=photo_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        photo_service=photo_service
    )
    
    update_photo_use_case = UpdatePhotoUseCase(
        photo_repository=photo_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        photo_service=photo_service
    )
    
    delete_photo_use_case = DeletePhotoUseCase(
        photo_repository=photo_repo,
        photo_service=photo_service,
        upload_service=upload_service
    )
    
    like_photo_use_case = LikePhotoUseCase(
        photo_repository=photo_repo,
        trip_member_repository=trip_member_repo,
        photo_service=photo_service
    )
    
    get_photo_gallery_use_case = GetPhotoGalleryUseCase(
        photo_repository=photo_repo,
        trip_member_repository=trip_member_repo,
        photo_service=photo_service
    )
    
    return PhotoController(
        create_photo_use_case=create_photo_use_case,
        get_photo_use_case=get_photo_use_case,
        get_trip_photos_use_case=get_trip_photos_use_case,
        update_photo_use_case=update_photo_use_case,
        delete_photo_use_case=delete_photo_use_case,
        like_photo_use_case=like_photo_use_case,
        get_photo_gallery_use_case=get_photo_gallery_use_case
    )

@router.post("/trips/{trip_id}/photos")
async def create_photo(
    trip_id: str = Path(...),
    file: UploadFile = File(...),
    day_id: Optional[str] = Form(None),
    diary_entry_id: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    controller: PhotoController = Depends(get_photo_controller)
):
    """Subir nueva foto al viaje"""
    # Convertir tags de string a lista
    tags_list = tags.split(",") if tags else []
    
    dto = CreatePhotoDTO(
        trip_id=trip_id,
        day_id=day_id,
        diary_entry_id=diary_entry_id,
        title=title,
        description=description,
        location=location,
        tags=tags_list
    )
    
    return await controller.create_photo(file, dto, current_user)

@router.get("/photos/{photo_id}")
async def get_photo(
    photo_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: PhotoController = Depends(get_photo_controller)
):
    """Obtener foto por ID"""
    return await controller.get_photo(photo_id, current_user)

@router.get("/trips/{trip_id}/photos")
async def get_trip_photos(
    trip_id: str = Path(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    day_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    controller: PhotoController = Depends(get_photo_controller)
):
    """Obtener fotos de un viaje"""
    return await controller.get_trip_photos(trip_id, current_user, limit, offset, day_id)

@router.put("/photos/{photo_id}")
async def update_photo(
    photo_id: str = Path(...),
    dto: UpdatePhotoDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: PhotoController = Depends(get_photo_controller)
):
    """Actualizar información de foto"""
    return await controller.update_photo(photo_id, dto, current_user)

@router.delete("/photos/{photo_id}")
async def delete_photo(
    photo_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: PhotoController = Depends(get_photo_controller)
):
    """Eliminar foto"""
    return await controller.delete_photo(photo_id, current_user)

@router.post("/photos/{photo_id}/like")
async def like_photo(
    photo_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: PhotoController = Depends(get_photo_controller)
):
    """Dar/quitar like a foto"""
    return await controller.like_photo(photo_id, current_user)

@router.get("/trips/{trip_id}/photos/gallery")
async def get_photo_gallery(
    trip_id: str = Path(...),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    controller: PhotoController = Depends(get_photo_controller)
):
    """Obtener galería organizada de fotos"""
    return await controller.get_photo_gallery(trip_id, current_user, limit, offset)