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
            
            # Generar nuevo ObjectId si no existe
            if "_id" not in document or not document["_id"]:
                document["_id"] = ObjectId()
            
            result = await self._collection.insert_one(document)
            
            # Actualizar el day con el ID real
            day_data.id = str(result.inserted_id)
            return Day.from_data(day_data)
            
        except Exception as e:
            print(f"[ERROR] Error creando día: {str(e)}")
            raise Exception(f"Error creando día: {str(e)}")

    async def find_by_id(self, day_id: str) -> Optional[Day]:
        """Buscar día por ID"""
        try:
            if not ObjectId.is_valid(day_id):
                return None
                
            document = await self._collection.find_one({
                "_id": ObjectId(day_id),
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
            
            await self._collection.update_one(
                {"_id": ObjectId(day.id)},
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
                {"_id": ObjectId(day_id)},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"[ERROR] Error eliminando día: {str(e)}")
            return False

    async def find_by_trip_id(self, trip_id: str) -> List[Day]:
        """Buscar días por viaje"""
        try:
            query = {
                "trip_id": trip_id,
                "is_deleted": {"$ne": True}
            }
            
            cursor = self._collection.find(query).sort("date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_day(doc) for doc in documents if doc]
        except Exception as e:
            print(f"[ERROR] Error buscando días del viaje: {str(e)}")
            return []

    async def find_by_trip_id_ordered(self, trip_id: str) -> List[Day]:
        """Buscar días por viaje ordenados por fecha"""
        return await self.find_by_trip_id(trip_id)

    async def find_by_trip_and_date(self, trip_id: str, day_date: date) -> Optional[Day]:
        """Buscar día específico por viaje y fecha"""
        try:
            # ✅ Convertir date a datetime para la consulta
            if isinstance(day_date, date) and not isinstance(day_date, datetime):
                date_query = datetime.combine(day_date, datetime.min.time())
            else:
                date_query = day_date
                
            document = await self._collection.find_one({
                "trip_id": trip_id,
                "date": date_query,  # ✅ Usar datetime para consulta
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_day(document) if document else None
        except Exception as e:
            print(f"[ERROR] Error buscando día por fecha: {str(e)}")
            return None

    async def find_by_date_range(
        self, 
        trip_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Day]:
        """Buscar días en rango de fechas"""
        try:
            # ✅ Convertir dates a datetime para MongoDB
            start_datetime = datetime.combine(start_date, datetime.min.time()) if isinstance(start_date, date) else start_date
            end_datetime = datetime.combine(end_date, datetime.max.time()) if isinstance(end_date, date) else end_date
            
            query = {
                "trip_id": trip_id,
                "date": {
                    "$gte": start_datetime,
                    "$lte": end_datetime
                },
                "is_deleted": {"$ne": True}
            }
            
            cursor = self._collection.find(query).sort("date", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_day(doc) for doc in documents if doc]
        except Exception as e:
            print(f"[ERROR] Error buscando días por rango: {str(e)}")
            return []

    async def find_with_notes(self, trip_id: str) -> List[Day]:
        """Buscar días que tienen notas"""
        try:
            query = {
                "trip_id": trip_id,
                "notes": {"$exists": True, "$ne": None, "$ne": ""},
                "is_deleted": {"$ne": True}
            }
            
            cursor = self._collection.find(query).sort("date", 1)
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
            
            # Aplicar filtros
            if "trip_id" in filters:
                query["trip_id"] = filters["trip_id"]
            
            if "has_notes" in filters:
                if filters["has_notes"]:
                    query["notes"] = {"$exists": True, "$ne": None, "$ne": ""}
                else:
                    query["$or"] = [
                        {"notes": {"$exists": False}},
                        {"notes": None},
                        {"notes": ""}
                    ]
            
            if "date_from" in filters:
                date_from = filters["date_from"]
                if isinstance(date_from, date) and not isinstance(date_from, datetime):
                    date_from = datetime.combine(date_from, datetime.min.time())
                query.setdefault("date", {})["$gte"] = date_from
                
            if "date_to" in filters:
                date_to = filters["date_to"]
                if isinstance(date_to, date) and not isinstance(date_to, datetime):
                    date_to = datetime.combine(date_to, datetime.max.time())
                query.setdefault("date", {})["$lte"] = date_to
            
            # Calcular skip para paginación
            skip = (page - 1) * limit
            
            # Ejecutar consulta con paginación
            cursor = self._collection.find(query).sort("date", 1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Contar total
            total = await self._collection.count_documents(query)
            
            days = [self._document_to_day(doc) for doc in documents if doc]
            return days, total
            
        except Exception as e:
            print(f"[ERROR] Error buscando días con filtros: {str(e)}")
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
            # ✅ Convertir date a datetime para la consulta
            if isinstance(day_date, date) and not isinstance(day_date, datetime):
                date_query = datetime.combine(day_date, datetime.min.time())
            else:
                date_query = day_date
                
            count = await self._collection.count_documents({
                "trip_id": trip_id,
                "date": date_query,  # ✅ Usar datetime para consulta
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
                if "_id" not in doc or not doc["_id"]:
                    doc["_id"] = ObjectId()
                documents.append(doc)
            
            result = await self._collection.insert_many(documents)
            
            # Actualizar los días con sus IDs reales
            created_days = []
            for i, day in enumerate(days):
                day_data = day.to_public_data()
                day_data.id = str(result.inserted_ids[i])
                created_days.append(Day.from_data(day_data))
            
            return created_days
            
        except Exception as e:
            print(f"[ERROR] Error en bulk_create: {str(e)}")
            raise Exception(f"Error creando días en lote: {str(e)}")

    async def get_trip_day_statistics(self, trip_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de días del viaje"""
        try:
            pipeline = [
                {
                    "$match": {
                        "trip_id": trip_id,
                        "is_deleted": {"$ne": True}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_days": {"$sum": 1},
                        "days_with_notes": {
                            "$sum": {
                                "$cond": [
                                    {
                                        "$and": [
                                            {"$ne": ["$notes", None]},
                                            {"$ne": ["$notes", ""]}
                                        ]
                                    },
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                }
            ]
            
            result = await self._collection.aggregate(pipeline).to_list(length=1)
            
            if not result:
                return {
                    "total_days": 0,
                    "days_with_notes": 0,
                    "completion_percentage": 0.0
                }
            
            stats = result[0]
            total = stats.get("total_days", 0)
            with_notes = stats.get("days_with_notes", 0)
            
            return {
                "total_days": total,
                "days_with_notes": with_notes,
                "completion_percentage": (with_notes / total * 100) if total > 0 else 0.0
            }
            
        except Exception as e:
            print(f"[ERROR] Error obteniendo estadísticas: {str(e)}")
            return {
                "total_days": 0,
                "days_with_notes": 0,
                "completion_percentage": 0.0
            }

    def _day_to_document(self, day_data: DayData) -> Dict[str, Any]:
        """Convertir DayData a documento MongoDB"""
        # ✅ Convertir date a datetime para MongoDB
        date_value = day_data.date
        if isinstance(date_value, date) and not isinstance(date_value, datetime):
            date_value = datetime.combine(date_value, datetime.min.time())
        
        doc = {
            "trip_id": day_data.trip_id,
            "date": date_value,  # ✅ Usar datetime convertido
            "notes": day_data.notes,
            "is_deleted": day_data.is_deleted or False,
            "created_at": day_data.created_at or datetime.utcnow(),
            "updated_at": day_data.updated_at or datetime.utcnow()
        }
        
        # Solo incluir _id si existe y es válido
        if day_data.id and ObjectId.is_valid(day_data.id):
            doc["_id"] = ObjectId(day_data.id)
        
        return {k: v for k, v in doc.items() if v is not None}

    def _document_to_day(self, document: Dict[str, Any]) -> Day:
        """Convertir documento MongoDB a Day"""
        try:
            # ✅ Convertir datetime de vuelta a date si es necesario
            date_value = document["date"]
            if isinstance(date_value, datetime):
                date_value = date_value.date()
            
            day_data = DayData(
                id=str(document["_id"]),
                trip_id=document["trip_id"],
                date=date_value,  # ✅ Usar date convertido
                notes=document.get("notes"),
                is_deleted=document.get("is_deleted", False),
                created_at=document.get("created_at", datetime.utcnow()),
                updated_at=document.get("updated_at", datetime.utcnow())
            )
            
            return Day.from_data(day_data)
        except Exception as e:
            print(f"[ERROR] Error convirtiendo documento a Day: {str(e)}")
            raise Exception(f"Error procesando día: {str(e)}")