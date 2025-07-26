from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List
from ..controllers.UploadController import UploadController
from ..middleware.AuthMiddleware import get_current_user

router = APIRouter(prefix="/api/upload")

def get_upload_controller():
    return UploadController()

@router.post("/profile-picture", summary="Subir foto de perfil")
async def upload_profile_picture(
    file: UploadFile = File(...),
    controller: UploadController = Depends(get_upload_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir o actualizar foto de perfil del usuario.
    
    - **file**: Archivo de imagen (JPG, PNG, WebP, GIF)
    - **Tamaño máximo**: 5MB
    - **Resolución**: Se redimensiona automáticamente a 400x400px
    - **Optimización**: Compresión automática y conversión a WebP
    
    La imagen anterior se reemplaza automáticamente.
    """
    return await controller.upload_profile_picture(file, current_user)

@router.post("/trip-photos/{trip_id}", summary="Subir fotos de viaje")
async def upload_trip_photos(
    trip_id: str,
    files: List[UploadFile] = File(...),
    controller: UploadController = Depends(get_upload_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir múltiples fotos para un viaje específico.
    
    - **trip_id**: ID del viaje al que pertenecen las fotos
    - **files**: Lista de archivos de imagen (máximo 10 por request)
    - **Tamaño máximo**: 5MB por archivo
    - **Resolución**: Se redimensiona a máximo 1200x800px
    - **Formatos**: JPG, PNG, WebP, GIF
    
    Las fotos se organizan automáticamente en carpetas por viaje.
    """
    return await controller.upload_trip_photos(trip_id, files, current_user)

@router.post("/document/{folder}", summary="Subir documento")
async def upload_document(
    folder: str,
    file: UploadFile = File(...),
    controller: UploadController = Depends(get_upload_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Subir documento a una carpeta específica.
    
    - **folder**: Nombre de la carpeta destino (ej: "itineraries", "tickets")
    - **file**: Archivo de documento
    - **Tamaño máximo**: 10MB
    - **Formatos**: PDF, DOC, DOCX, TXT
    
    Útil para subir itinerarios, tickets, reservas, etc.
    """
    return await controller.upload_document(folder, file, current_user)

@router.delete("/file/{public_id}", summary="Eliminar archivo")
async def delete_file(
    public_id: str,
    resource_type: str = "image",
    controller: UploadController = Depends(get_upload_controller),
    current_user: dict = Depends(get_current_user)
):
    """
    Eliminar archivo de Cloudinary.
    
    - **public_id**: ID público del archivo en Cloudinary
    - **resource_type**: Tipo de recurso ("image", "raw", "video")
    
    ⚠️ **Advertencia**: Esta acción es irreversible.
    """
    return await controller.delete_file(public_id, resource_type, current_user)