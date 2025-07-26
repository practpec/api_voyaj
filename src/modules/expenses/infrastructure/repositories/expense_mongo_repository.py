from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from ...domain.expense import Expense, ExpenseData, ExpenseCategory, ExpenseStatus
from ...domain.interfaces.expense_repository_interface import ExpenseRepositoryInterface
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class ExpenseMongoRepository(ExpenseRepositoryInterface):
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "expenses"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Obtener colección de gastos"""
        database = await self._db_connection.get_database()
        return database[self._collection_name]

    def _to_expense_entity(self, document: Dict[str, Any]) -> Expense:
        """Convertir documento MongoDB a entidad Expense"""
        if not document:
            return None

        data = ExpenseData(
            id=document["_id"],
            trip_id=document["trip_id"],
            user_id=document["user_id"],
            activity_id=document.get("activity_id"),
            diary_entry_id=document.get("diary_entry_id"),
            amount=document["amount"],
            currency=document["currency"],
            category=ExpenseCategory(document["category"]),
            description=document["description"],
            receipt_url=document.get("receipt_url"),
            location=document.get("location"),
            expense_date=document["expense_date"],
            is_shared=document.get("is_shared", False),
            paid_by_user_id=document["paid_by_user_id"],
            status=ExpenseStatus(document.get("status", "pending")),
            metadata=document.get("metadata", {}),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        return Expense(data)

    def _to_document(self, expense: Expense) -> Dict[str, Any]:
        """Convertir entidad Expense a documento MongoDB"""
        data = expense.to_public_data()
        return {
            "_id": data.id,
            "trip_id": data.trip_id,
            "user_id": data.user_id,
            "activity_id": data.activity_id,
            "diary_entry_id": data.diary_entry_id,
            "amount": float(data.amount),
            "currency": data.currency,
            "category": data.category.value,
            "description": data.description,
            "receipt_url": data.receipt_url,
            "location": data.location,
            "expense_date": data.expense_date,
            "is_shared": data.is_shared,
            "paid_by_user_id": data.paid_by_user_id,
            "status": data.status.value,
            "metadata": data.metadata,
            "is_deleted": data.is_deleted,
            "created_at": data.created_at,
            "updated_at": data.updated_at
        }

    async def save(self, expense: Expense) -> None:
        """Guardar gasto"""
        try:
            collection = await self._get_collection()
            document = self._to_document(expense)
            await collection.insert_one(document)
        except Exception as e:
            raise DatabaseError(f"Error al guardar gasto: {str(e)}")

    async def find_by_id(self, expense_id: str) -> Optional[Expense]:
        """Buscar gasto por ID"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({"_id": expense_id})
            return self._to_expense_entity(document) if document else None
        except Exception as e:
            raise DatabaseError(f"Error al buscar gasto: {str(e)}")

    async def find_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos por ID de viaje"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"trip_id": trip_id})
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos por viaje: {str(e)}")

    async def find_by_trip_and_user_id(self, trip_id: str, user_id: str) -> List[Expense]:
        """Buscar gastos por viaje y usuario"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "trip_id": trip_id,
                "user_id": user_id
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos por viaje y usuario: {str(e)}")

    async def find_shared_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos compartidos por viaje"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "trip_id": trip_id,
                "is_shared": True
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos compartidos: {str(e)}")

    async def find_by_activity_id(self, activity_id: str) -> List[Expense]:
        """Buscar gastos por actividad"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"activity_id": activity_id})
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos por actividad: {str(e)}")

    async def find_by_diary_entry_id(self, diary_entry_id: str) -> List[Expense]:
        """Buscar gastos por entrada de diario"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"diary_entry_id": diary_entry_id})
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos por entrada de diario: {str(e)}")

    async def find_by_trip_id_and_date_range(
        self, 
        trip_id: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Expense]:
        """Buscar gastos por viaje y rango de fechas"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "trip_id": trip_id,
                "expense_date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos por fecha: {str(e)}")

    async def find_by_category_and_date_range(
        self, 
        trip_id: str, 
        category: ExpenseCategory, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Expense]:
        """Buscar gastos por categoría y rango de fechas"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "trip_id": trip_id,
                "category": category.value,
                "expense_date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos por categoría: {str(e)}")

    async def find_by_paid_by_user_id(self, trip_id: str, user_id: str) -> List[Expense]:
        """Buscar gastos pagados por usuario específico"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "trip_id": trip_id,
                "paid_by_user_id": user_id
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos pagados por usuario: {str(e)}")

    async def update(self, expense: Expense) -> None:
        """Actualizar gasto"""
        try:
            collection = await self._get_collection()
            document = self._to_document(expense)
            result = await collection.replace_one(
                {"_id": expense.id},
                document
            )
            if result.matched_count == 0:
                raise DatabaseError("Gasto no encontrado para actualizar")
        except Exception as e:
            raise DatabaseError(f"Error al actualizar gasto: {str(e)}")

    async def delete(self, expense_id: str) -> None:
        """Eliminar gasto (soft delete)"""
        try:
            collection = await self._get_collection()
            result = await collection.update_one(
                {"_id": expense_id},
                {
                    "$set": {
                        "is_deleted": True,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            if result.matched_count == 0:
                raise DatabaseError("Gasto no encontrado para eliminar")
        except Exception as e:
            raise DatabaseError(f"Error al eliminar gasto: {str(e)}")

    async def exists_by_id(self, expense_id: str) -> bool:
        """Verificar si existe gasto por ID"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({"_id": expense_id})
            return count > 0
        except Exception as e:
            raise DatabaseError(f"Error al verificar existencia de gasto: {str(e)}")

    async def count_by_trip_id(self, trip_id: str) -> int:
        """Contar gastos activos por viaje"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "trip_id": trip_id,
                "is_deleted": False
            })
            return count
        except Exception as e:
            raise DatabaseError(f"Error al contar gastos: {str(e)}")

    async def find_with_receipt_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos que tienen comprobante"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "trip_id": trip_id,
                "receipt_url": {"$ne": None, "$exists": True}
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos con comprobante: {str(e)}")

    async def find_without_receipt_by_trip_id(self, trip_id: str) -> List[Expense]:
        """Buscar gastos sin comprobante"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "trip_id": trip_id,
                "$or": [
                    {"receipt_url": None},
                    {"receipt_url": {"$exists": False}}
                ]
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar gastos sin comprobante: {str(e)}")