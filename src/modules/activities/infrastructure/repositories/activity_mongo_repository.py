# src/modules/activities/infrastructure/repositories/activity_mongo_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from shared.database.Connection import DatabaseConnection
from ...domain.activity import Activity
from ...domain.interfaces.activity_repository import IActivityRepository


class ActivityMongoRepository(IActivityRepository):
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "actividades"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Obtener colección de actividades"""
        database = await self._db_connection.get_database()
        return database[self._collection_name]

    async def create(self, activity: Activity) -> Activity:
        """Crear nueva actividad"""
        collection = await self._get_collection()
        activity_data = activity.to_dict()
        await collection.insert_one(activity_data)
        return activity

    async def find_by_id(self, activity_id: str) -> Optional[Activity]:
        """Buscar actividad por ID"""
        collection = await self._get_collection()
        activity_data = await collection.find_one({
            "id": activity_id,
            "deleted_at": None
        })
        
        if activity_data:
            return Activity.from_dict(activity_data)
        return None

    async def update(self, activity: Activity) -> Activity:
        """Actualizar actividad"""
        collection = await self._get_collection()
        activity_data = activity.to_dict()
        activity_data["updated_at"] = datetime.utcnow()
        
        await collection.update_one(
            {"id": activity.id},
            {"$set": activity_data}
        )
        return activity

    async def delete(self, activity_id: str) -> bool:
        """Eliminar actividad (soft delete)"""
        collection = await self._get_collection()
        result = await collection.update_one(
            {"id": activity_id},
            {"$set": {
                "deleted_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }}
        )
        return result.modified_count > 0

    async def find_by_day_id(self, day_id: str) -> List[Activity]:
        """Buscar actividades por día"""
        collection = await self._get_collection()
        cursor = collection.find({
            "day_id": day_id,
            "deleted_at": None
        })
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities

    async def find_by_day_id_ordered(self, day_id: str) -> List[Activity]:
        """Buscar actividades por día ordenadas"""
        collection = await self._get_collection()
        cursor = collection.find({
            "day_id": day_id,
            "deleted_at": None
        }).sort("order", 1)
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities

    async def find_by_trip_id(self, trip_id: str) -> List[Activity]:
        """Buscar actividades por viaje"""
        collection = await self._get_collection()
        cursor = collection.find({
            "trip_id": trip_id,
            "deleted_at": None
        }).sort([("day_id", 1), ("order", 1)])
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities

    async def find_by_status(self, day_id: str, status: str) -> List[Activity]:
        """Buscar actividades por estado"""
        collection = await self._get_collection()
        cursor = collection.find({
            "day_id": day_id,
            "status": status,
            "deleted_at": None
        }).sort("order", 1)
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities

    async def find_by_category(self, day_id: str, category: str) -> List[Activity]:
        """Buscar actividades por categoría"""
        collection = await self._get_collection()
        cursor = collection.find({
            "day_id": day_id,
            "category": category,
            "deleted_at": None
        }).sort("order", 1)
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities

    async def find_by_user(self, user_id: str, trip_id: Optional[str] = None) -> List[Activity]:
        """Buscar actividades creadas por usuario"""
        collection = await self._get_collection()
        query = {
            "created_by": user_id,
            "deleted_at": None
        }
        
        if trip_id:
            query["trip_id"] = trip_id
            
        cursor = collection.find(query).sort("created_at", -1)
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Activity], int]:
        """Buscar actividades con filtros y paginación"""
        collection = await self._get_collection()
        query = {"deleted_at": None}
        
        # Aplicar filtros
        if "day_id" in filters:
            query["day_id"] = filters["day_id"]
        if "trip_id" in filters:
            query["trip_id"] = filters["trip_id"]
        if "status" in filters:
            query["status"] = filters["status"]
        if "category" in filters:
            query["category"] = filters["category"]
        if "priority" in filters:
            query["priority"] = filters["priority"]
        if "created_by" in filters:
            query["created_by"] = filters["created_by"]
        if "tags" in filters:
            query["tags"] = {"$in": filters["tags"]}
        
        # Filtros de rango de fechas
        if "date_from" in filters:
            query["created_at"] = {"$gte": filters["date_from"]}
        if "date_to" in filters:
            if "created_at" not in query:
                query["created_at"] = {}
            query["created_at"]["$lte"] = filters["date_to"]
        
        # Contar total
        total = await collection.count_documents(query)
        
        # Calcular offset
        skip = (page - 1) * limit
        
        # Buscar con paginación
        cursor = collection.find(query).sort("order", 1).skip(skip).limit(limit)
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities, total

    async def count_by_day_id(self, day_id: str) -> int:
        """Contar actividades por día"""
        collection = await self._get_collection()
        return await collection.count_documents({
            "day_id": day_id,
            "deleted_at": None
        })

    async def count_by_status(self, day_id: str, status: str) -> int:
        """Contar actividades por estado"""
        collection = await self._get_collection()
        return await collection.count_documents({
            "day_id": day_id,
            "status": status,
            "deleted_at": None
        })

    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar actividades por viaje"""
        collection = await self._get_collection()
        return await collection.count_documents({
            "trip_id": trip_id,
            "deleted_at": None
        })

    async def get_next_order(self, day_id: str) -> int:
        """Obtener siguiente número de orden para el día"""
        collection = await self._get_collection()
        # Buscar la actividad con el orden más alto
        result = await collection.find_one(
            {"day_id": day_id, "deleted_at": None},
            sort=[("order", -1)]
        )
        
        if result:
            return result.get("order", 0) + 1
        return 1