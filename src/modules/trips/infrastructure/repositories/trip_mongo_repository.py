# src/modules/trips/infrastructure/repositories/trip_mongo_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from ...domain.trip import Trip, TripData, TripStatus
from ...domain.interfaces.trip_repository import Trip
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class TripMongoRepository(Trip):
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "trips"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Obtener colección de viajes"""
        database = self._db_connection.get_database()
        return database[self._collection_name]

    def _document_to_trip(self, document: Dict[str, Any]) -> Trip:
        """Convertir documento MongoDB a entidad Trip"""
        if not document:
            return None

        data = TripData(
            id=str(document["_id"]),
            owner_id=document["owner_id"],
            title=document["title"],
            description=document.get("description", ""),
            destination=document["destination"],
            start_date=document["start_date"],
            end_date=document["end_date"],
            estimated_budget=document.get("estimated_budget", 0.0),
            actual_expenses=document.get("actual_expenses", 0.0),
            base_currency=document.get("base_currency", "USD"),
            is_group_trip=document.get("is_group_trip", False),
            status=TripStatus(document.get("status", "planning")),
            category=document.get("category", "vacation"),
            image=document.get("image", "🗺️"),
            planning_progress=document.get("planning_progress", 0),
            notes=document.get("notes", ""),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        return Trip(data)

    def _trip_to_document(self, trip_data: TripData) -> Dict[str, Any]:
        """Convertir entidad Trip a documento MongoDB"""
        return {
            "_id": trip_data.id,
            "owner_id": trip_data.owner_id,
            "title": trip_data.title,
            "description": trip_data.description,
            "destination": trip_data.destination,
            "start_date": trip_data.start_date,
            "end_date": trip_data.end_date,
            "estimated_budget": trip_data.estimated_budget,
            "actual_expenses": trip_data.actual_expenses,
            "base_currency": trip_data.base_currency,
            "is_group_trip": trip_data.is_group_trip,
            "status": trip_data.status.value,
            "category": trip_data.category,
            "image": trip_data.image,
            "planning_progress": trip_data.planning_progress,
            "notes": trip_data.notes,
            "is_deleted": trip_data.is_deleted,
            "created_at": trip_data.created_at,
            "updated_at": trip_data.updated_at
        }

    async def save(self, trip: Trip) -> Trip:
        """Guardar viaje"""
        try:
            collection = await self._get_collection()
            document = self._trip_to_document(trip.to_data())
            
            await collection.insert_one(document)
            return trip
            
        except Exception as error:
            raise DatabaseError(f"Error guardando viaje: {str(error)}")

    async def update(self, trip: Trip) -> Trip:
        """Actualizar viaje"""
        try:
            collection = await self._get_collection()
            document = self._trip_to_document(trip.to_data())
            
            await collection.update_one(
                {"_id": trip.id},
                {"$set": document}
            )
            return trip
            
        except Exception as error:
            raise DatabaseError(f"Error actualizando viaje: {str(error)}")

    async def find_by_id(self, trip_id: str) -> Optional[Trip]:
        """Buscar viaje por ID"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "_id": trip_id,
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_trip(document) if document else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viaje por ID: {str(error)}")

    async def find_by_owner_id(
        self, 
        owner_id: str, 
        page: int = 1, 
        limit: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[Trip], int]:
        """Buscar viajes por propietario"""
        try:
            collection = await self._get_collection()
            
            query = {
                "owner_id": owner_id,
                "is_deleted": {"$ne": True}
            }
            
            if status:
                query["status"] = status
            
            skip = (page - 1) * limit
            
            cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            total = await collection.count_documents(query)
            
            trips = [self._document_to_trip(doc) for doc in documents]
            return trips, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes por propietario: {str(error)}")

    async def find_active_by_user_id(self, user_id: str) -> List[Trip]:
        """Buscar viajes activos de un usuario"""
        try:
            collection = await self._get_collection()
            
            query = {
                "owner_id": user_id,
                "status": {"$in": ["planning", "active"]},
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("start_date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes activos: {str(error)}")

    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        """Buscar viajes en un rango de fechas"""
        try:
            collection = await self._get_collection()
            
            query = {
                "$or": [
                    {"start_date": {"$gte": start_date, "$lte": end_date}},
                    {"end_date": {"$gte": start_date, "$lte": end_date}},
                    {"start_date": {"$lte": start_date}, "end_date": {"$gte": end_date}}
                ],
                "is_deleted": {"$ne": True}
            }
            
            if user_id:
                query["owner_id"] = user_id
            
            cursor = collection.find(query).sort("start_date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes por fecha: {str(error)}")

    async def delete(self, trip_id: str) -> bool:
        """Eliminar viaje (soft delete)"""
        try:
            collection = await self._get_collection()
            
            result = await collection.update_one(
                {"_id": trip_id},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error eliminando viaje: {str(error)}")

    async def exists(self, trip_id: str) -> bool:
        """Verificar si existe un viaje"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "_id": trip_id,
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception:
            return False

    async def search(
        self, 
        query: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        """Buscar viajes por texto"""
        try:
            collection = await self._get_collection()
            
            search_query = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}},
                    {"destination": {"$regex": query, "$options": "i"}},
                    {"notes": {"$regex": query, "$options": "i"}}
                ],
                "is_deleted": {"$ne": True}
            }
            
            if user_id:
                search_query["owner_id"] = user_id
            
            cursor = collection.find(search_query).sort("created_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error en búsqueda de viajes: {str(error)}")

    async def get_user_trip_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de viajes de un usuario"""
        try:
            collection = await self._get_collection()
            
            pipeline = [
                {
                    "$match": {
                        "owner_id": user_id,
                        "is_deleted": {"$ne": True}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_trips": {"$sum": 1},
                        "completed_trips": {
                            "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                        },
                        "active_trips": {
                            "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                        },
                        "total_expenses": {"$sum": "$actual_expenses"},
                        "destinations": {"$addToSet": "$destination"},
                        "categories": {"$push": "$category"},
                        "avg_duration": {
                            "$avg": {
                                "$divide": [
                                    {"$subtract": ["$end_date", "$start_date"]},
                                    86400000
                                ]
                            }
                        }
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if not result:
                return {
                    "total_trips": 0,
                    "completed_trips": 0,
                    "active_trips": 0,
                    "total_expenses": 0.0,
                    "average_trip_duration": 0.0
                }
            
            stats = result[0]
            return {
                "total_trips": stats.get("total_trips", 0),
                "completed_trips": stats.get("completed_trips", 0),
                "active_trips": stats.get("active_trips", 0),
                "total_expenses": stats.get("total_expenses", 0.0),
                "average_trip_duration": stats.get("avg_duration", 0.0)
            }
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo estadísticas: {str(error)}")
        
    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Trip], int]:
        """Buscar viajes con filtros y paginación"""
        try:
            collection = await self._get_collection()
            query = {"is_deleted": {"$ne": True}}
            
            # Aplicar filtros
            if filters.get("owner_id"):
                query["owner_id"] = filters["owner_id"]
            
            if filters.get("status"):
                query["status"] = filters["status"]
            
            if filters.get("category"):
                query["category"] = filters["category"]
            
            if filters.get("is_group_trip") is not None:
                query["is_group_trip"] = filters["is_group_trip"]
            
            if filters.get("destination"):
                query["destination"] = {"$regex": filters["destination"], "$options": "i"}
            
            if filters.get("start_date") and filters.get("end_date"):
                query["start_date"] = {"$gte": filters["start_date"]}
                query["end_date"] = {"$lte": filters["end_date"]}
            elif filters.get("start_date"):
                query["start_date"] = {"$gte": filters["start_date"]}
            elif filters.get("end_date"):
                query["end_date"] = {"$lte": filters["end_date"]}
            
            if filters.get("min_budget") is not None:
                query["estimated_budget"] = {"$gte": filters["min_budget"]}
            
            if filters.get("max_budget") is not None:
                if "estimated_budget" in query:
                    query["estimated_budget"]["$lte"] = filters["max_budget"]
                else:
                    query["estimated_budget"] = {"$lte": filters["max_budget"]}
            
            # Paginación
            skip = (page - 1) * limit
            
            # Ejecutar consulta con paginación
            cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Contar total de documentos
            total = await collection.count_documents(query)
            
            # Convertir documentos a entidades
            trips = [self._document_to_trip(doc) for doc in documents]
            
            return trips, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes con filtros: {str(error)}")

    async def count_by_filters(self, filters: Dict[str, Any]) -> int:
        """Contar viajes con filtros"""
        try:
            collection = await self._get_collection()
            query = {"is_deleted": {"$ne": True}}
            
            # Aplicar los mismos filtros que en find_with_filters
            if filters.get("owner_id"):
                query["owner_id"] = filters["owner_id"]
            
            if filters.get("status"):
                query["status"] = filters["status"]
            
            if filters.get("category"):
                query["category"] = filters["category"]
            
            if filters.get("is_group_trip") is not None:
                query["is_group_trip"] = filters["is_group_trip"]
            
            if filters.get("destination"):
                query["destination"] = {"$regex": filters["destination"], "$options": "i"}
            
            if filters.get("start_date") and filters.get("end_date"):
                query["start_date"] = {"$gte": filters["start_date"]}
                query["end_date"] = {"$lte": filters["end_date"]}
            elif filters.get("start_date"):
                query["start_date"] = {"$gte": filters["start_date"]}
            elif filters.get("end_date"):
                query["end_date"] = {"$lte": filters["end_date"]}
            
            if filters.get("min_budget") is not None:
                query["estimated_budget"] = {"$gte": filters["min_budget"]}
            
            if filters.get("max_budget") is not None:
                if "estimated_budget" in query:
                    query["estimated_budget"]["$lte"] = filters["max_budget"]
                else:
                    query["estimated_budget"] = {"$lte": filters["max_budget"]}
            
            return await collection.count_documents(query)
            
        except Exception:
            return 0

    async def exists_by_id(self, trip_id: str) -> bool:
        """Verificar si existe un viaje por ID"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "_id": trip_id,
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception:
            return False

    async def is_owner(self, trip_id: str, user_id: str) -> bool:
        """Verificar si el usuario es propietario del viaje"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "_id": trip_id,
                "owner_id": user_id,
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception:
            return False

    async def get_user_trip_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de viajes del usuario"""
        try:
            collection = await self._get_collection()
            
            # Consulta de agregación para obtener estadísticas
            pipeline = [
                {
                    "$match": {
                        "owner_id": user_id,
                        "is_deleted": {"$ne": True}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_trips": {"$sum": 1},
                        "total_budget": {"$sum": "$estimated_budget"},
                        "total_expenses": {"$sum": "$actual_expenses"},
                        "completed_trips": {
                            "$sum": {
                                "$cond": [{"$eq": ["$status", "completed"]}, 1, 0]
                            }
                        },
                        "in_progress_trips": {
                            "$sum": {
                                "$cond": [{"$eq": ["$status", "in_progress"]}, 1, 0]
                            }
                        },
                        "planned_trips": {
                            "$sum": {
                                "$cond": [{"$eq": ["$status", "planning"]}, 1, 0]
                            }
                        },
                        "group_trips": {
                            "$sum": {
                                "$cond": [{"$eq": ["$is_group_trip", True]}, 1, 0]
                            }
                        }
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                stats = result[0]
                stats.pop("_id", None)
                return stats
            else:
                return {
                    "total_trips": 0,
                    "total_budget": 0.0,
                    "total_expenses": 0.0,
                    "completed_trips": 0,
                    "in_progress_trips": 0,
                    "planned_trips": 0,
                    "group_trips": 0
                }
                
        except Exception as error:
            raise DatabaseError(f"Error obteniendo estadísticas del usuario: {str(error)}")

    async def create(self, trip: Trip) -> Trip:
        """Crear nuevo viaje"""
        try:
            collection = await self._get_collection()
            document = self._trip_to_document(trip.to_data())
            
            await collection.insert_one(document)
            return trip
            
        except Exception as error:
            raise DatabaseError(f"Error creando viaje: {str(error)}")

    async def find_active_by_owner_id(self, owner_id: str) -> List[Trip]:
        """Buscar viajes activos por propietario"""
        try:
            collection = await self._get_collection()
            query = {
                "owner_id": owner_id,
                "status": {"$in": ["planning", "in_progress"]},
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("start_date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes activos: {str(error)}")

    async def find_by_destination(
        self, 
        destination: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        """Buscar viajes por destino"""
        try:
            collection = await self._get_collection()
            query = {
                "destination": {"$regex": destination, "$options": "i"},
                "is_deleted": {"$ne": True}
            }
            
            if user_id:
                query["owner_id"] = user_id
            
            cursor = collection.find(query).sort("start_date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes por destino: {str(error)}")

    async def find_by_category(
        self, 
        category: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        """Buscar viajes por categoría"""
        try:
            collection = await self._get_collection()
            query = {
                "category": category,
                "is_deleted": {"$ne": True}
            }
            
            if user_id:
                query["owner_id"] = user_id
            
            cursor = collection.find(query).sort("start_date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes por categoría: {str(error)}")

    async def find_group_trips_by_user(self, user_id: str) -> List[Trip]:
        """Buscar viajes grupales del usuario"""
        try:
            collection = await self._get_collection()
            query = {
                "owner_id": user_id,
                "is_group_trip": True,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("start_date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes grupales: {str(error)}")