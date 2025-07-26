# src/modules/photos/domain/Photo.py
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

class Photo:
    """Entidad de dominio para Photo"""
    
    def __init__(
        self,
        trip_id: str,
        user_id: str,
        url: str,
        public_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        day_id: Optional[str] = None,
        diary_entry_id: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        file_size: Optional[int] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        taken_at: Optional[datetime] = None,
        likes: Optional[List[str]] = None,
        uploaded_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        id: Optional[str] = None
    ):
        self.id = id or str(ObjectId())
        self.trip_id = trip_id
        self.user_id = user_id
        self.day_id = day_id
        self.diary_entry_id = diary_entry_id
        self.title = title
        self.description = description
        self.location = location
        self.tags = tags or []
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.public_id = public_id
        self.file_size = file_size
        self.width = width
        self.height = height
        self.taken_at = taken_at
        self.likes = likes or []
        self.uploaded_at = uploaded_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def add_like(self, user_id: str) -> bool:
        """Agregar like de usuario"""
        if user_id not in self.likes:
            self.likes.append(user_id)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def remove_like(self, user_id: str) -> bool:
        """Quitar like de usuario"""
        if user_id in self.likes:
            self.likes.remove(user_id)
            self.updated_at = datetime.utcnow()
            return True
        return False

    def has_like_from(self, user_id: str) -> bool:
        """Verificar si usuario ya dio like"""
        return user_id in self.likes

    def get_likes_count(self) -> int:
        """Obtener cantidad de likes"""
        return len(self.likes)

    def update_info(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        tags: Optional[List[str]] = None,
        day_id: Optional[str] = None,
        diary_entry_id: Optional[str] = None
    ):
        """Actualizar información de la foto"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if location is not None:
            self.location = location
        if tags is not None:
            self.tags = tags
        if day_id is not None:
            self.day_id = day_id
        if diary_entry_id is not None:
            self.diary_entry_id = diary_entry_id
        
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        return {
            "_id": self.id,
            "trip_id": self.trip_id,
            "user_id": self.user_id,
            "day_id": self.day_id,
            "diary_entry_id": self.diary_entry_id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "tags": self.tags,
            "url": self.url,
            "thumbnail_url": self.thumbnail_url,
            "public_id": self.public_id,
            "file_size": self.file_size,
            "width": self.width,
            "height": self.height,
            "taken_at": self.taken_at,
            "likes": self.likes,
            "uploaded_at": self.uploaded_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Photo":
        """Crear instancia desde diccionario"""
        return cls(
            id=str(data.get("_id", "")),
            trip_id=data.get("trip_id"),
            user_id=data.get("user_id"),
            day_id=data.get("day_id"),
            diary_entry_id=data.get("diary_entry_id"),
            title=data.get("title"),
            description=data.get("description"),
            location=data.get("location"),
            tags=data.get("tags", []),
            url=data.get("url"),
            thumbnail_url=data.get("thumbnail_url"),
            public_id=data.get("public_id"),
            file_size=data.get("file_size"),
            width=data.get("width"),
            height=data.get("height"),
            taken_at=data.get("taken_at"),
            likes=data.get("likes", []),
            uploaded_at=data.get("uploaded_at"),
            updated_at=data.get("updated_at")
        )