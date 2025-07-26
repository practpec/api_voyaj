# src/modules/photos/application/dtos/photo_dto.py
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

class CreatePhotoDTO(BaseModel):
    """DTO para crear nueva foto"""
    trip_id: str = Field(..., description="ID del viaje")
    day_id: Optional[str] = Field(None, description="ID del día (opcional)")
    diary_entry_id: Optional[str] = Field(None, description="ID de entrada de diario (opcional)")
    title: Optional[str] = Field(None, max_length=200, description="Título de la foto")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción de la foto")
    location: Optional[str] = Field(None, max_length=300, description="Ubicación donde se tomó")
    tags: Optional[List[str]] = Field([], description="Etiquetas de la foto")

class UpdatePhotoDTO(BaseModel):
    """DTO para actualizar información de foto"""
    title: Optional[str] = Field(None, max_length=200, description="Título de la foto")
    description: Optional[str] = Field(None, max_length=1000, description="Descripción de la foto")
    location: Optional[str] = Field(None, max_length=300, description="Ubicación donde se tomó")
    tags: Optional[List[str]] = Field(None, description="Etiquetas de la foto")
    day_id: Optional[str] = Field(None, description="ID del día (para reasignar)")
    diary_entry_id: Optional[str] = Field(None, description="ID de entrada de diario")

class PhotoResponseDTO(BaseModel):
    """DTO de respuesta para foto"""
    id: str
    trip_id: str
    user_id: str
    day_id: Optional[str]
    diary_entry_id: Optional[str]
    title: Optional[str]
    description: Optional[str]
    location: Optional[str]
    tags: List[str]
    url: str
    thumbnail_url: Optional[str]
    public_id: str
    file_size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    taken_at: Optional[datetime]
    likes_count: int
    is_liked: Optional[bool]
    uploaded_at: datetime
    updated_at: datetime

class BulkUploadDTO(BaseModel):
    """DTO para subida masiva de fotos"""
    trip_id: str = Field(..., description="ID del viaje")
    day_id: Optional[str] = Field(None, description="ID del día para todas las fotos")
    default_tags: Optional[List[str]] = Field([], description="Etiquetas por defecto")

class LikePhotoDTO(BaseModel):
    """DTO para dar/quitar like a foto"""
    photo_id: str = Field(..., description="ID de la foto")

class PhotoGalleryResponseDTO(BaseModel):
    """DTO para respuesta de galería"""
    photos: List[PhotoResponseDTO]
    total: int
    page: int
    limit: int
    has_more: bool

class PhotoStatsDTO(BaseModel):
    """DTO para estadísticas de fotos"""
    total_photos: int
    photos_by_day: Dict[str, int]
    most_liked_photo: Optional[PhotoResponseDTO]
    recent_photos: List[PhotoResponseDTO]