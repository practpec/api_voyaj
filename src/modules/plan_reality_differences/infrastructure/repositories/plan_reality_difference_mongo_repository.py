from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection

from ...domain.PlanRealityDifference import PlanRealityDifferenceData
from ...domain.interfaces.IPlanRealityDifferenceRepository import IPlanRealityDifferenceRepository
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class PlanRealityDifferenceMongoRepository(IPlanRealityDifferenceRepository):
    """Implementación MongoDB del repositorio de diferencias plan vs realidad"""
    
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "plan_reality_differences"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Obtener colección de diferencias plan vs realidad"""
        database = await self._db_connection.get_database()
        return database[self._collection_name]

    async def save(self, difference: PlanRealityDifferenceData) -> PlanRealityDifferenceData:
        """Guardar diferencia"""
        collection = await self._get_collection()
        document = self._to_document(difference)
        await collection.insert_one(document)
        return difference

    async def find_by_id(self, difference_id: str) -> Optional[PlanRealityDifferenceData]:
        """Buscar diferencia por ID"""
        collection = await self._get_collection()
        document = await collection.find_one({
            "_id": difference_id,
            "is_deleted": {"$ne": True}
        })
        
        if not document:
            return None
        
        return self._to_entity(document)

    async def find_by_trip_id(self, trip_id: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por ID del viaje"""
        collection = await self._get_collection()
        cursor = collection.find({
            "trip_id": trip_id,
            "is_deleted": {"$ne": True}
        }).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    async def find_by_day_id(self, day_id: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por ID del día"""
        collection = await self._get_collection()
        cursor = collection.find({
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        }).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    async def find_by_activity_id(self, activity_id: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por ID de la actividad"""
        collection = await self._get_collection()
        cursor = collection.find({
            "activity_id": activity_id,
            "is_deleted": {"$ne": True}
        }).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    async def find_by_trip_and_metric(self, trip_id: str, metric: str) -> List[PlanRealityDifferenceData]:
        """Buscar diferencias por viaje y métrica específica"""
        collection = await self._get_collection()
        cursor = collection.find({
            "trip_id": trip_id,
            "metric": metric,
            "is_deleted": {"$ne": True}
        }).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._to_entity(doc) for doc in documents]

    async def update(self, difference: PlanRealityDifferenceData) -> PlanRealityDifferenceData:
        """Actualizar diferencia"""
        collection = await self._get_collection()
        document = self._to_document(difference)
        
        await collection.update_one(
            {"_id": difference.id},
            {"$set": document}
        )
        
        return difference

    async def delete(self, difference_id: str) -> bool:
        """Eliminar diferencia (soft delete)"""
        collection = await self._get_collection()
        result = await collection.update_one(
            {"_id": difference_id},
            {
                "$set": {
                    "is_deleted": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0

    async def exists_by_id(self, difference_id: str) -> bool:
        """Verificar si existe una diferencia por ID"""
        collection = await self._get_collection()
        count = await collection.count_documents({
            "_id": difference_id,
            "is_deleted": {"$ne": True}
        })
        
        return count > 0

    def _to_document(self, difference: PlanRealityDifferenceData) -> Dict[str, Any]:
        """Convertir entidad a documento MongoDB"""
        return {
            "_id": difference.id,
            "trip_id": difference.trip_id,
            "day_id": difference.day_id,
            "activity_id": difference.activity_id,
            "metric": difference.metric,
            "planned_value": difference.planned_value,
            "actual_value": difference.actual_value,
            "notes": difference.notes,
            "is_deleted": difference.is_deleted,
            "created_at": difference.created_at,
            "updated_at": difference.updated_at
        }

    def _to_entity(self, document: Dict[str, Any]) -> PlanRealityDifferenceData:
        """Convertir documento MongoDB a entidad"""
        return PlanRealityDifferenceData(
            id=document["_id"],
            trip_id=document["trip_id"],
            day_id=document.get("day_id"),
            activity_id=document.get("activity_id"),
            metric=document["metric"],
            planned_value=document["planned_value"],
            actual_value=document["actual_value"],
            notes=document.get("notes"),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )