# src/modules/trips/infrastructure/repositories/trip_mongo_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from ...domain.trip import Trip, TripData, TripStatus
from ...domain.interfaces.trip_repository import ITripRepository
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class TripMongoRepository(ITripRepository):
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
            category=document.get("category", "leisure"),
            status=document.get("status", "planning"),
            is_group_trip=document.get("is_group_trip", False),
            is_public=document.get("is_public", False),
            budget_limit=document.get("budget_limit"),
            currency=document.get("currency", "USD"),
            image_url=document.get("image_url"),
            notes=document.get("notes", ""),
            total_expenses=document.get("total_expenses", 0.0),
            member_count=document.get("member_count", 1),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        return Trip.from_data(data)

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
            "category": trip_data.category,
            "status": trip_data.status,
            "is_group_trip": trip_data.is_group_trip,
            "is_public": trip_data.is_public,
            "budget_limit": trip_data.budget_limit,
            "currency": trip_data.currency,
            "image_url": trip_data.image_url,
            "notes": trip_data.notes,
            "total_expenses": trip_data.total_expenses,
            "member_count": trip_data.member_count,
            "is_deleted": trip_data.is_deleted,
            "created_at": trip_data.created_at,
            "updated_at": trip_data.updated_at
        }

    async def save(self, trip: Trip) -> Trip:
        """Guardar viaje"""
        try:
            collection = await self._get_collection()
            document = self._trip_to_document(trip.to_public_data())
            
            await collection.insert_one(document)
            return trip
            
        except Exception as error:
            raise DatabaseError(f"Error guardando viaje: {str(error)}")

    async def update(self, trip: Trip) -> Trip:
        """Actualizar viaje"""
        try:
            collection = await self._get_collection()
            document = self._trip_to_document(trip.to_public_data())
            document.pop("_id", None)  # Remover ID para evitar conflictos
            
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
            
            # Contar total de documentos
            total = await collection.count_documents(query)
            
            # Obtener viajes paginados
            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            documents = await cursor.to_list(length=limit)
            
            trips = [self._document_to_trip(doc) for doc in documents if doc]
            
            return trips, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes por propietario: {str(error)}")

    async def find_by_user_participation(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Trip], int]:
        """Buscar viajes donde el usuario participa (como owner o miembro)"""
        try:
            collection = await self._get_collection()
            
            # Pipeline de agregación para unir con trip_members
            pipeline = [
                {
                    "$lookup": {
                        "from": "trip_members",
                        "localField": "_id",
                        "foreignField": "trip_id",
                        "as": "members"
                    }
                },
                {
                    "$match": {
                        "$and": [
                            {"is_deleted": {"$ne": True}},
                            {
                                "$or": [
                                    {"owner_id": user_id},
                                    {
                                        "members": {
                                            "$elemMatch": {
                                                "user_id": user_id,
                                                "status": {"$in": ["pending", "accepted"]},
                                                "is_deleted": {"$ne": True}
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
            
            # Aplicar filtros adicionales si se proporcionan
            if filters:
                additional_match = {}
                if filters.get("status"):
                    additional_match["status"] = filters["status"]
                if filters.get("category"):
                    additional_match["category"] = filters["category"]
                if filters.get("is_group_trip") is not None:
                    additional_match["is_group_trip"] = filters["is_group_trip"]
                if filters.get("destination"):
                    additional_match["destination"] = {"$regex": filters["destination"], "$options": "i"}
                
                if additional_match:
                    pipeline.append({"$match": additional_match})
            
            # Contar total
            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = await collection.aggregate(count_pipeline).to_list(1)
            total = count_result[0]["total"] if count_result else 0
            
            # Obtener resultados paginados
            skip = (page - 1) * limit
            pipeline.extend([
                {"$sort": {"created_at": -1}},
                {"$skip": skip},
                {"$limit": limit},
                {"$project": {"members": 0}}  # Excluir members del resultado
            ])
            
            documents = await collection.aggregate(pipeline).to_list(limit)
            trips = [self._document_to_trip(doc) for doc in documents if doc]
            
            return trips, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes por participación: {str(error)}")

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

    async def count_by_owner(self, owner_id: str) -> int:
        """Contar viajes por propietario"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "owner_id": owner_id,
                "is_deleted": {"$ne": True}
            })
            
            return count
            
        except Exception as error:
            raise DatabaseError(f"Error contando viajes: {str(error)}")

    async def update_expenses(self, trip_id: str, new_total: float) -> bool:
        """Actualizar total de gastos del viaje"""
        try:
            collection = await self._get_collection()
            result = await collection.update_one(
                {"_id": trip_id},
                {
                    "$set": {
                        "actual_expenses": new_total,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error actualizando gastos del viaje: {str(error)}")

    async def update_planning_progress(self, trip_id: str, progress: int) -> bool:
        """Actualizar progreso de planificación"""
        try:
            collection = await self._get_collection()
            result = await collection.update_one(
                {"_id": trip_id},
                {
                    "$set": {
                        "planning_progress": max(0, min(100, progress)),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error actualizando progreso de planificación: {str(error)}")

    # MÉTODOS ABSTRACTOS REQUERIDOS POR ITripRepository

    async def create(self, trip: Trip) -> Trip:
        """Crear nuevo viaje - alias para save()"""
        return await self.save(trip)

    async def find_active_by_owner_id(self, owner_id: str) -> List[Trip]:
        """Buscar viajes activos por propietario"""
        try:
            collection = await self._get_collection()
            query = {
                "owner_id": owner_id,
                "is_deleted": {"$ne": True},
                "status": {"$ne": "cancelled"}
            }
            
            cursor = collection.find(query).sort("created_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_trip(doc) for doc in documents if doc]
            
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
                query["$or"] = [
                    {"owner_id": user_id},
                    {"is_public": True}
                ]
            
            cursor = collection.find(query).sort("created_at", -1)
            documents = await cursor.to_list(length=50)
            
            return [self._document_to_trip(doc) for doc in documents if doc]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando por destino: {str(error)}")

    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        """Buscar viajes por rango de fechas"""
        try:
            collection = await self._get_collection()
            query = {
                "$and": [
                    {"start_date": {"$gte": start_date}},
                    {"end_date": {"$lte": end_date}},
                    {"is_deleted": {"$ne": True}}
                ]
            }
            
            if user_id:
                query["$or"] = [
                    {"owner_id": user_id},
                    {"is_public": True}
                ]
            
            cursor = collection.find(query).sort("start_date", 1)
            documents = await cursor.to_list(length=100)
            
            return [self._document_to_trip(doc) for doc in documents if doc]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando por rango de fechas: {str(error)}")

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
                query["$or"] = [
                    {"owner_id": user_id},
                    {"is_public": True}
                ]
            
            cursor = collection.find(query).sort("created_at", -1)
            documents = await cursor.to_list(length=50)
            
            return [self._document_to_trip(doc) for doc in documents if doc]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando por categoría: {str(error)}")

    async def find_group_trips_by_user(self, user_id: str) -> List[Trip]:
        """Buscar viajes grupales donde participa el usuario"""
        try:
            collection = await self._get_collection()
            
            # Pipeline para buscar viajes donde el usuario es miembro
            pipeline = [
                {
                    "$lookup": {
                        "from": "trip_members",
                        "localField": "_id",
                        "foreignField": "trip_id",
                        "as": "members"
                    }
                },
                {
                    "$match": {
                        "$and": [
                            {"is_group_trip": True},
                            {"is_deleted": {"$ne": True}},
                            {
                                "$or": [
                                    {"owner_id": user_id},
                                    {
                                        "members": {
                                            "$elemMatch": {
                                                "user_id": user_id,
                                                "status": "accepted",
                                                "is_deleted": {"$ne": True}
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                },
                {"$project": {"members": 0}},
                {"$sort": {"created_at": -1}}
            ]
            
            documents = await collection.aggregate(pipeline).to_list(100)
            return [self._document_to_trip(doc) for doc in documents if doc]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes grupales: {str(error)}")

    async def search(
        self, 
        query: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        """Buscar viajes por texto"""
        try:
            collection = await self._get_collection()
            
            search_query = {
                "$and": [
                    {
                        "$or": [
                            {"title": {"$regex": query, "$options": "i"}},
                            {"description": {"$regex": query, "$options": "i"}},
                            {"destination": {"$regex": query, "$options": "i"}},
                            {"notes": {"$regex": query, "$options": "i"}}
                        ]
                    },
                    {"is_deleted": {"$ne": True}}
                ]
            }
            
            if user_id:
                search_query["$and"].append({
                    "$or": [
                        {"owner_id": user_id},
                        {"is_public": True}
                    ]
                })
            
            cursor = collection.find(search_query).sort("created_at", -1)
            documents = await cursor.to_list(length=50)
            
            return [self._document_to_trip(doc) for doc in documents if doc]
            
        except Exception as error:
            raise DatabaseError(f"Error en búsqueda de texto: {str(error)}")

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
            if filters.get("start_date"):
                query["start_date"] = {"$gte": filters["start_date"]}
            if filters.get("end_date"):
                query["end_date"] = {"$lte": filters["end_date"]}
            
            # Contar total
            total = await collection.count_documents(query)
            
            # Obtener resultados paginados
            skip = (page - 1) * limit
            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            documents = await cursor.to_list(length=limit)
            
            trips = [self._document_to_trip(doc) for doc in documents if doc]
            
            return trips, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando con filtros: {str(error)}")

    async def count_by_filters(self, filters: Dict[str, Any]) -> int:
        """Contar viajes que coinciden con los filtros"""
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
            
            return await collection.count_documents(query)
            
        except Exception as error:
            raise DatabaseError(f"Error contando con filtros: {str(error)}")

    async def exists_by_id(self, trip_id: str) -> bool:
        """Verificar si existe un viaje por ID"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "_id": trip_id,
                "is_deleted": {"$ne": True}
            })
            
            return count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error verificando existencia: {str(error)}")

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
            
        except Exception as error:
            raise DatabaseError(f"Error verificando propietario: {str(error)}")

    async def get_user_trip_stats(self, user_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de viajes del usuario"""
        try:
            collection = await self._get_collection()
            
            # Pipeline de agregación para estadísticas
            pipeline = [
                {
                    "$lookup": {
                        "from": "trip_members",
                        "localField": "_id",
                        "foreignField": "trip_id",
                        "as": "members"
                    }
                },
                {
                    "$match": {
                        "$and": [
                            {"is_deleted": {"$ne": True}},
                            {
                                "$or": [
                                    {"owner_id": user_id},
                                    {
                                        "members": {
                                            "$elemMatch": {
                                                "user_id": user_id,
                                                "status": "accepted",
                                                "is_deleted": {"$ne": True}
                                            }
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_trips": {"$sum": 1},
                        "owned_trips": {
                            "$sum": {
                                "$cond": [{"$eq": ["$owner_id", user_id]}, 1, 0]
                            }
                        },
                        "group_trips": {
                            "$sum": {
                                "$cond": ["$is_group_trip", 1, 0]
                            }
                        },
                        "completed_trips": {
                            "$sum": {
                                "$cond": [{"$eq": ["$status", "completed"]}, 1, 0]
                            }
                        },
                        "active_trips": {
                            "$sum": {
                                "$cond": [{"$eq": ["$status", "active"]}, 1, 0]
                            }
                        },
                        "total_budget": {"$sum": "$estimated_budget"},
                        "total_expenses": {"$sum": "$actual_expenses"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(1)
            
            if result:
                stats = result[0]
                stats.pop("_id", None)
                return stats
            else:
                return {
                    "total_trips": 0,
                    "owned_trips": 0,
                    "group_trips": 0,
                    "completed_trips": 0,
                    "active_trips": 0,
                    "total_budget": 0.0,
                    "total_expenses": 0.0
                }
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo estadísticas: {str(error)}")