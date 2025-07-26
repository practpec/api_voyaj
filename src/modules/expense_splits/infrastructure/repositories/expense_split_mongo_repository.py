from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from decimal import Decimal
from ...domain.expense_split import ExpenseSplit, ExpenseSplitData, ExpenseSplitStatus
from ...domain.interfaces.expense_split_repository_interface import ExpenseSplitRepositoryInterface
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class ExpenseSplitMongoRepository(ExpenseSplitRepositoryInterface):
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "expense_splits"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Obtener colección de divisiones de gastos"""
        database = await self._db_connection.get_database()
        return database[self._collection_name]

    def _to_expense_split_entity(self, document: Dict[str, Any]) -> ExpenseSplit:
        """Convertir documento MongoDB a entidad ExpenseSplit"""
        if not document:
            return None

        data = ExpenseSplitData(
            id=document["_id"],
            expense_id=document["expense_id"],
            user_id=document["user_id"],
            amount=Decimal(str(document["amount"])),
            status=ExpenseSplitStatus(document.get("status", "pending")),
            paid_at=document.get("paid_at"),
            notes=document.get("notes"),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        return ExpenseSplit(data)

    def _to_document(self, expense_split: ExpenseSplit) -> Dict[str, Any]:
        """Convertir entidad ExpenseSplit a documento MongoDB"""
        data = expense_split.to_public_data()
        return {
            "_id": data.id,
            "expense_id": data.expense_id,
            "user_id": data.user_id,
            "amount": float(data.amount),
            "status": data.status.value,
            "paid_at": data.paid_at,
            "notes": data.notes,
            "is_deleted": data.is_deleted,
            "created_at": data.created_at,
            "updated_at": data.updated_at
        }

    async def create(self, expense_split: ExpenseSplit) -> ExpenseSplit:
        """Crear nueva división de gasto"""
        try:
            collection = await self._get_collection()
            document = self._to_document(expense_split)
            await collection.insert_one(document)
            return expense_split
        except Exception as e:
            raise DatabaseError(f"Error al crear división de gasto: {str(e)}")

    async def find_by_id(self, expense_split_id: str) -> Optional[ExpenseSplit]:
        """Buscar división por ID"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({"_id": expense_split_id})
            return self._to_expense_split_entity(document) if document else None
        except Exception as e:
            raise DatabaseError(f"Error al buscar división: {str(e)}")

    async def find_by_expense_id(self, expense_id: str) -> List[ExpenseSplit]:
        """Buscar divisiones por ID de gasto"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"expense_id": expense_id, "is_deleted": False})
            documents = await cursor.to_list(length=None)
            return [self._to_expense_split_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar divisiones por gasto: {str(e)}")

    async def find_by_user_id(self, user_id: str) -> List[ExpenseSplit]:
        """Buscar divisiones por ID de usuario"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"user_id": user_id, "is_deleted": False})
            documents = await cursor.to_list(length=None)
            return [self._to_expense_split_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar divisiones por usuario: {str(e)}")

    async def find_by_expense_and_user(self, expense_id: str, user_id: str) -> Optional[ExpenseSplit]:
        """Buscar división específica por gasto y usuario"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "expense_id": expense_id,
                "user_id": user_id,
                "is_deleted": False
            })
            return self._to_expense_split_entity(document) if document else None
        except Exception as e:
            raise DatabaseError(f"Error al buscar división específica: {str(e)}")

    async def update(self, expense_split: ExpenseSplit) -> ExpenseSplit:
        """Actualizar división de gasto"""
        try:
            collection = await self._get_collection()
            document = self._to_document(expense_split)
            await collection.replace_one({"_id": expense_split.id}, document)
            return expense_split
        except Exception as e:
            raise DatabaseError(f"Error al actualizar división: {str(e)}")

    async def delete(self, expense_split_id: str) -> bool:
        """Eliminar división de gasto"""
        try:
            collection = await self._get_collection()
            result = await collection.update_one(
                {"_id": expense_split_id},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error al eliminar división: {str(e)}")

    async def delete_by_expense_id(self, expense_id: str) -> bool:
        """Eliminar todas las divisiones de un gasto"""
        try:
            collection = await self._get_collection()
            result = await collection.update_many(
                {"expense_id": expense_id},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error al eliminar divisiones del gasto: {str(e)}")

    async def get_user_pending_splits(self, user_id: str) -> List[ExpenseSplit]:
        """Obtener divisiones pendientes de un usuario"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "user_id": user_id,
                "status": "pending",
                "is_deleted": False
            })
            documents = await cursor.to_list(length=None)
            return [self._to_expense_split_entity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error al buscar divisiones pendientes: {str(e)}")

    async def get_trip_balances(self, trip_id: str) -> List[dict]:
        """Obtener balances de usuarios en un viaje"""
        try:
            collection = await self._get_collection()
            pipeline = [
                {
                    "$lookup": {
                        "from": "expenses",
                        "localField": "expense_id",
                        "foreignField": "_id",
                        "as": "expense"
                    }
                },
                {
                    "$unwind": "$expense"
                },
                {
                    "$match": {
                        "expense.trip_id": trip_id,
                        "is_deleted": False
                    }
                },
                {
                    "$group": {
                        "_id": "$user_id",
                        "amount_owed": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$status", "pending"]},
                                    "$amount",
                                    0
                                ]
                            }
                        },
                        "amount_paid": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$status", "paid"]},
                                    "$amount",
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "user_id": "$_id",
                        "amount_owed": 1,
                        "amount_paid": 1
                    }
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            raise DatabaseError(f"Error al calcular balances del viaje: {str(e)}")