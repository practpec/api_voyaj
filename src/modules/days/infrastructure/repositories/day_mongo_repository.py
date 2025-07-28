# src/modules/days/infrastructure/repositories/day_mongo_repository.py
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ...domain.Day import Day, DayData
from ...domain.interfaces.day_repository import IDayRepository
from shared.database.Connection import DatabaseConnection


class DayMongoRepository(IDayRepository):
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self._db = db or DatabaseConnection.get_database()
        self._collection = self._db.days

    async def create(self, day: Day) -> Day:
        """Crear nuevo día"""
        try:
            day_data = day.to_public_data()
            document = self._day_to_document(day_data)
            
            # ✅ CORREGIDO: No generar ObjectId, usar el ID string del dominio
            await self._collection.insert_one(document)
            return day
            
        except Exception as e:
            print(f"[ERROR] Error creando día: {str(e)}")
            raise Exception(f"Error creando día: {str(e)}")

    async def find_by_id(self, day_id: str) -> Optional[Day]:
        """Buscar día por ID"""
        try:
            # ✅ CORREGIDO: Buscar por string ID, no ObjectId
            document = await self._collection.find_one({
                "_id": day_id,
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_day(document) if document else None
        except Exception as e:
            print(f"[ERROR] Error buscando día {day_id}: {str(e)}")
            return None

    async def update(self, day: Day) -> Day:
        """Actualizar día existente"""
        try:
            day_data = self._day_to_document(day.to_public_data())
            day_data.pop("_id", None)
            day_data["updated_at"] = datetime.utcnow()
            
            # ✅ CORREGIDO: Usar string ID, no ObjectId
            await self._collection.update_one(
                {"_id": day.id},
                {"$set": day_data}
            )
            
            return day
            
        except Exception as e:
            print(f"[ERROR] Error actualizando día: {str(e)}")
            raise Exception(f"Error actualizando día: {str(e)}")

    async def delete(self, day_id: str) -> bool:
        """Eliminar día (soft delete)"""
        try:
            result = await self._collection.update_one(
                {"_id": day_id},  # ✅ CORREGIDO: string ID
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error eliminando día: {str(e)}")
            return False

    async def find_by_trip_id(self, trip_id: str) -> List[Day]:
        """Buscar días por viaje"""
        try:
            cursor = self._collection.find({
                "trip_id": trip_id,
                "is_deleted": {"$ne": True}
            }).sort("date", 1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_day(doc) for doc in documents if doc]
        except Exception as e:
            print(f"[ERROR] Error buscando días por viaje: {str(e)}")
            return []

    async def find_by_trip_id_ordered(self, trip_id: str) -> List[Day]:
        """Buscar días por viaje ordenados por fecha"""
        try:
            cursor = self._collection.find({
                "trip_id": trip_id,
                "is_deleted": {"$ne": True}
            }).sort("date", 1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_day(doc) for doc in documents if doc]
        except Exception as e:
            print(f"[ERROR] Error buscando días ordenados: {str(e)}")
            return []

    async def find_by_trip_and_date(self, trip_id: str, day_date: date) -> Optional[Day]:
        """Buscar día específico por viaje y fecha"""
        try:
            if isinstance(day_date, date) and not isinstance(day_date, datetime):
                date_query = datetime.combine(day_date, datetime.min.time())
            else:
                date_query = day_date
                
            document = await self._collection.find_one({
                "trip_id": trip_id,
                "date": date_query,
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_day(document) if document else None
        except Exception as e:
            print(f"[ERROR] Error buscando por fecha: {str(e)}")
            return None

    async def find_by_date_range(
        self, 
        trip_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Day]:
        """Buscar días en rango de fechas"""
        try:
            if isinstance(start_date, date) and not isinstance(start_date, datetime):
                start_query = datetime.combine(start_date, datetime.min.time())
            else:
                start_query = start_date
                
            if isinstance(end_date, date) and not isinstance(end_date, datetime):
                end_query = datetime.combine(end_date, datetime.max.time())
            else:
                end_query = end_date

            cursor = self._collection.find({
                "trip_id": trip_id,
                "date": {"$gte": start_query, "$lte": end_query},
                "is_deleted": {"$ne": True}
            }).sort("date", 1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_day(doc) for doc in documents if doc]
        except Exception as e:
            print(f"[ERROR] Error buscando por rango de fechas: {str(e)}")
            return []

    async def find_with_notes(self, trip_id: str) -> List[Day]:
        """Buscar días que tienen notas"""
        try:
            cursor = self._collection.find({
                "trip_id": trip_id,
                "notes": {"$exists": True, "$ne": None, "$ne": ""},
                "is_deleted": {"$ne": True}
            }).sort("date", 1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_day(doc) for doc in documents if doc]
        except Exception as e:
            print(f"[ERROR] Error buscando días con notas: {str(e)}")
            return []

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Day], int]:
        """Buscar días con filtros y paginación"""
        try:
            query = {"is_deleted": {"$ne": True}}
            query.update(filters)
            
            skip = (page - 1) * limit
            cursor = self._collection.find(query).sort("date", 1).skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            total = await self._collection.count_documents(query)
            
            days = [self._document_to_day(doc) for doc in documents if doc]
            return days, total
        except Exception as e:
            print(f"[ERROR] Error buscando con filtros: {str(e)}")
            return [], 0

    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar días por viaje"""
        try:
            return await self._collection.count_documents({
                "trip_id": trip_id,
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            print(f"[ERROR] Error contando días: {str(e)}")
            return 0

    async def count_with_notes(self, trip_id: str) -> int:
        """Contar días con notas por viaje"""
        try:
            return await self._collection.count_documents({
                "trip_id": trip_id,
                "notes": {"$exists": True, "$ne": None, "$ne": ""},
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            print(f"[ERROR] Error contando días con notas: {str(e)}")
            return 0

    async def exists_by_trip_and_date(self, trip_id: str, day_date: date) -> bool:
        """Verificar si existe día para fecha específica"""
        try:
            if isinstance(day_date, date) and not isinstance(day_date, datetime):
                date_query = datetime.combine(day_date, datetime.min.time())
            else:
                date_query = day_date
                
            count = await self._collection.count_documents({
                "trip_id": trip_id,
                "date": date_query,
                "is_deleted": {"$ne": True}
            })
            
            return count > 0
        except Exception as e:
            print(f"[ERROR] Error verificando existencia: {str(e)}")
            return False

    async def delete_by_trip_id(self, trip_id: str) -> bool:
        """Eliminar todos los días de un viaje"""
        try:
            result = await self._collection.update_many(
                {"trip_id": trip_id},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error eliminando días del viaje: {str(e)}")
            return False

    async def bulk_create(self, days: List[Day]) -> List[Day]:
        """Crear múltiples días en lote"""
        if not days:
            return []
        
        try:
            documents = []
            for day in days:
                doc = self._day_to_document(day.to_public_data())
                # ✅ CORREGIDO: No generar ObjectId, usar el ID del dominio
                documents.append(doc)
            
            await self._collection.insert_many(documents)
            return days  # ✅ CORREGIDO: Retornar los días originales
            
        except Exception as e:
            print(f"[ERROR] Error en creación masiva: {str(e)}")
            return []

    async def get_trip_day_statistics(self, trip_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de días del viaje"""
        try:
            pipeline = [
                {"$match": {"trip_id": trip_id, "is_deleted": {"$ne": True}}},
                {
                    "$group": {
                        "_id": None,
                        "total_days": {"$sum": 1},
                        "days_with_notes": {
                            "$sum": {
                                "$cond": [
                                    {"$and": [
                                        {"$ne": ["$notes", None]},
                                        {"$ne": ["$notes", ""]}
                                    ]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "first_date": {"$min": "$date"},
                        "last_date": {"$max": "$date"}
                    }
                }
            ]
            
            cursor = self._collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            
            if result:
                stats = result[0]
                stats.pop("_id", None)
                return stats
            else:
                return {
                    "total_days": 0,
                    "days_with_notes": 0,
                    "first_date": None,
                    "last_date": None
                }
                
        except Exception as e:
            print(f"[ERROR] Error obteniendo estadísticas: {str(e)}")
            return {
                "total_days": 0,
                "days_with_notes": 0,
                "first_date": None,
                "last_date": None
            }

    # MÉTODOS AUXILIARES
    def _day_to_document(self, day_data: DayData) -> Dict[str, Any]:
        """Convertir entidad Day a documento MongoDB"""
        # ✅ CORREGIDO: Convertir date a datetime para MongoDB
        date_value = day_data.date
        if isinstance(date_value, date) and not isinstance(date_value, datetime):
            date_value = datetime.combine(date_value, datetime.min.time())
        
        return {
            "_id": day_data.id,
            "trip_id": day_data.trip_id,
            "date": date_value,  # ✅ datetime en lugar de date
            "notes": day_data.notes,
            "is_deleted": day_data.is_deleted or False,
            "created_at": day_data.created_at or datetime.utcnow(),
            "updated_at": day_data.updated_at or datetime.utcnow()
        }

    def _document_to_day(self, document: Dict[str, Any]) -> Day:
        """Convertir documento MongoDB a entidad Day"""
        # ✅ CORREGIDO: Convertir datetime de vuelta a date para el dominio
        date_value = document.get("date")
        if isinstance(date_value, datetime):
            date_value = date_value.date()
        
        day_data = DayData(
            id=str(document["_id"]),
            trip_id=document.get("trip_id"),
            date=date_value,  # ✅ date para el dominio
            notes=document.get("notes"),
            is_deleted=document.get("is_deleted", False),
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at")
        )
        
        return Day.from_data(day_data)