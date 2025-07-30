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
        # CORREGIDO: get_database() no necesita await
        database = self._db_connection.get_database()
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
            {"$set": {"deleted_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def find_by_day_id(self, day_id: str) -> List[Activity]:
        """Buscar actividades por día"""
        collection = await self._get_collection()
        cursor = collection.find({
            "day_id": day_id,
            "deleted_at": None
        }).sort("order", 1)
        
        activities = []
        async for activity_data in cursor:
            activities.append(Activity.from_dict(activity_data))
        
        return activities

    async def find_by_day_id_ordered(self, day_id: str) -> List[Activity]:
        """Buscar actividades por día ordenadas"""
        return await self.find_by_day_id(day_id)

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
            
        cursor = collection.find(query).sort([("trip_id", 1), ("day_id", 1), ("order", 1)])
        
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
        if "trip_id" in filters:
            query["trip_id"] = filters["trip_id"]
        if "day_id" in filters:
            query["day_id"] = filters["day_id"]
        if "status" in filters:
            query["status"] = filters["status"]
        if "category" in filters:
            query["category"] = filters["category"]
        if "created_by" in filters:
            query["created_by"] = filters["created_by"]
        
        # Contar total
        total = await collection.count_documents(query)
        
        # Obtener resultados paginados
        skip = (page - 1) * limit
        cursor = collection.find(query).sort([("day_id", 1), ("order", 1)]).skip(skip).limit(limit)
        
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
        
        # Buscar la actividad con el orden más alto del día
        cursor = collection.find({
            "day_id": day_id,
            "deleted_at": None
        }).sort("order", -1).limit(1)
        
        async for activity_data in cursor:
            return activity_data.get("order", 0) + 1
        
        # Si no hay actividades, empezar en 1
        return 1

    async def update_orders(self, day_id: str, activity_orders: List[Dict[str, Any]]) -> bool:
        """Actualizar órdenes de actividades"""
        collection = await self._get_collection()
        
        for order_item in activity_orders:
            await collection.update_one(
                {"id": order_item["activity_id"], "day_id": day_id},
                {"$set": {"order": order_item["order"], "updated_at": datetime.utcnow()}}
            )
        
        return True