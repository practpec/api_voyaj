from pydantic import BaseModel
from typing import List, Optional

class UploadResponseDTO(BaseModel):
    url: str
    public_id: str
    message: str = "Archivo subido exitosamente"

class MultipleUploadResponseDTO(BaseModel):
    files: List[UploadResponseDTO]
    total_uploaded: int
    message: str = "Archivos subidos exitosamente"

class ProfilePictureUploadDTO(BaseModel):
    url: str
    public_id: str
    message: str = "Foto de perfil actualizada exitosamente"

class TripPhotoUploadDTO(BaseModel):
    url: str
    public_id: str
    original_name: Optional[str] = None
    message: str = "Foto de viaje subida exitosamente"

class DocumentUploadDTO(BaseModel):
    url: str
    public_id: str
    original_name: str
    file_type: str
    message: str = "Documento subido exitosamente"