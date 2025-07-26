# src/modules/photos/infrastructure/repositories/photo_mongo_repository.py
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from shared.database.Connection import DatabaseConnection
from ...domain.interfaces.IPhotoRepository import IPhotoRepository
from ...domain.Photo import Photo
from datetime import datetime

class PhotoMongoRepository(IPhotoRepository):
    """Implementación MongoDB del repositorio de fotos"""

    def __init__(self):
        self.db = DatabaseConnection()
        self.collection: AsyncIOMotorCollection = None

    async def _get_collection(self) -> AsyncIOMotorCollection:
        if not self.collection:
            database = await self.db.get_database()
            self.collection = database.photos
        return self.collection

    async def create(self, photo: Photo) -> Photo:
        """Crear nueva foto"""
        collection = await self._get_collection()
        photo_dict = photo.to_dict()
        
        result = await collection.insert_one(photo_dict)
        photo.id = str(result.inserted_id)
        
        return photo

    async def get_by_id(self, photo_id: str) -> Optional[Photo]:
        """Obtener foto por ID"""
        collection = await self._get_collection()
        
        photo_data = await collection.find_one({"_id": photo_id})
        
        if photo_data:
            return Photo.from_dict(photo_data)
        return None

    async def get_by_trip_id(
        self, 
        trip_id: str, 
        limit: int = 20, 
        offset: int = 0,
        day_id: Optional[str] = None
    ) -> List[Photo]:
        """Obtener fotos de un viaje"""
        collection = await self._get_collection()
        
        query = {"trip_id": trip_id}
        if day_id:
            query["day_id"] = day_id
            
        cursor = collection.find(query)\
            .sort("uploaded_at", -1)\
            .skip(offset)\
            .limit(limit)
        
        photos = []
        async for photo_data in cursor:
            photos.append(Photo.from_dict(photo_data))
        
        return photos

    async def get_by_day_id(self, day_id: str) -> List[Photo]:
        """Obtener fotos de un día específico"""
        collection = await self._get_collection()
        
        cursor = collection.find({"day_id": day_id})\
            .sort("uploaded_at", -1)
        
        photos = []
        async for photo_data in cursor:
            photos.append(Photo.from_dict(photo_data))
        
        return photos

    async def get_by_diary_entry_id(self, diary_entry_id: str) -> List[Photo]:
        """Obtener fotos de una entrada de diario"""
        collection = await self._get_collection()
        
        cursor = collection.find({"diary_entry_id": diary_entry_id})\
            .sort("uploaded_at", -1)
        
        photos = []
        async for photo_data in cursor:
            photos.append(Photo.from_dict(photo_data))
        
        return photos

    async def update(self, photo: Photo) -> Photo:
        """Actualizar foto"""
        collection = await self._get_collection()
        
        photo.updated_at = datetime.utcnow()
        photo_dict = photo.to_dict()
        photo_dict.pop("_id")
        
        await collection.update_one(
            {"_id": photo.id},
            {"$set": photo_dict}
        )
        
        return photo

    async def delete(self, photo_id: str) -> bool:
        """Eliminar foto"""
        collection = await self._get_collection()
        
        result = await collection.delete_one({"_id": photo_id})
        return result.deleted_count > 0

    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar fotos de un viaje"""
        collection = await self._get_collection()
        return await collection.count_documents({"trip_id": trip_id})

    async def get_trip_photos_stats(self, trip_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de fotos del viaje"""
        collection = await self._get_collection()
        
        # Estadísticas básicas
        total = await collection.count_documents({"trip_id": trip_id})
        
        # Fotos por día
        pipeline = [
            {"$match": {"trip_id": trip_id, "day_id": {"$ne": None}}},
            {"$group": {
                "_id": "$day_id",
                "count": {"$sum": 1}
            }}
        ]
        
        photos_by_day = {}
        async for doc in collection.aggregate(pipeline):
            if doc["_id"]:
                photos_by_day[doc["_id"]] = doc["count"]
        
        # Fotos recientes
        recent_cursor = collection.find({"trip_id": trip_id})\
            .sort("uploaded_at", -1)\
            .limit(5)
        
        recent = []
        async for photo_data in recent_cursor:
            recent.append(Photo.from_dict(photo_data))
        
        return {
            "total": total,
            "by_day": photos_by_day,
            "recent": recent
        }

    async def get_most_liked_photos(self, trip_id: str, limit: int = 5) -> List[Photo]:
        """Obtener fotos con más likes"""
        collection = await self._get_collection()
        
        pipeline = [
            {"$match": {"trip_id": trip_id}},
            {"$addFields": {"likes_count": {"$size": "$likes"}}},
            {"$sort": {"likes_count": -1, "uploaded_at": -1}},
            {"$limit": limit}
        ]
        
        photos = []
        async for photo_data in collection.aggregate(pipeline):
            photos.append(Photo.from_dict(photo_data))
        
        return photos

    async def search_photos(
        self, 
        trip_id: str, 
        query: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Photo]:
        """Buscar fotos por título, descripción o tags"""
        collection = await self._get_collection()
        
        search_query = {
            "trip_id": trip_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}},
                {"location": {"$regex": query, "$options": "i"}}
            ]
        }
        
        cursor = collection.find(search_query)\
            .sort("uploaded_at", -1)\
            .skip(offset)\
            .limit(limit)
        
        photos = []
        async for photo_data in cursor:
            photos.append(Photo.from_dict(photo_data))
        
        return photos