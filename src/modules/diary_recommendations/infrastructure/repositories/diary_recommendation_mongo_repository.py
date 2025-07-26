# src/modules/diary_recommendations/infrastructure/repositories/diary_recommendation_mongo_repository.py
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from ...domain.diary_recommendation import DiaryRecommendation, DiaryRecommendationData, RecommendationType
from ...domain.interfaces.diary_recommendation_repository_interface import DiaryRecommendationRepositoryInterface
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class DiaryRecommendationMongoRepository(DiaryRecommendationRepositoryInterface):
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "diary_recommendations"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Obtener colección de recomendaciones de diario"""
        database = await self._db_connection.get_database()
        return database[self._collection_name]

    def _to_entity(self, document: Dict[str, Any]) -> DiaryRecommendation:
        """Convertir documento MongoDB a entidad DiaryRecommendation"""
        if not document:
            return None

        data = DiaryRecommendationData(
            id=str(document["_id"]),
            diary_entry_id=document["diary_entry_id"],
            note=document["note"],
            type=RecommendationType(document["type"]),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        return DiaryRecommendation(data)

    def _to_document(self, recommendation: DiaryRecommendation) -> Dict[str, Any]:
        """Convertir entidad DiaryRecommendation a documento MongoDB"""
        data = recommendation.to_public_data()
        return {
            "_id": data.id,
            "diary_entry_id": data.diary_entry_id,
            "note": data.note,
            "type": data.type.value,
            "is_deleted": data.is_deleted,
            "created_at": data.created_at,
            "updated_at": data.updated_at
        }

    async def save(self, recommendation: DiaryRecommendation) -> None:
        """Guardar recomendación"""
        try:
            collection = await self._get_collection()
            document = self._to_document(recommendation)
            
            await collection.insert_one(document)

        except Exception as e:
            raise DatabaseError(f"Error al guardar recomendación: {str(e)}")

    async def find_by_id(self, recommendation_id: str) -> Optional[DiaryRecommendation]:
        """Buscar recomendación por ID"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({"_id": recommendation_id})
            
            return self._to_entity(document)

        except Exception as e:
            raise DatabaseError(f"Error al buscar recomendación: {str(e)}")

    async def find_by_diary_entry_id(self, diary_entry_id: str) -> List[DiaryRecommendation]:
        """Buscar recomendaciones por entrada de diario"""
        try:
            collection = await self._get_collection()
            cursor = collection.find({"diary_entry_id": diary_entry_id})
            
            recommendations = []
            async for document in cursor:
                recommendation = self._to_entity(document)
                if recommendation:
                    recommendations.append(recommendation)
            
            return recommendations

        except Exception as e:
            raise DatabaseError(f"Error al buscar recomendaciones por entrada: {str(e)}")

    async def update(self, recommendation: DiaryRecommendation) -> None:
        """Actualizar recomendación"""
        try:
            collection = await self._get_collection()
            document = self._to_document(recommendation)
            
            await collection.update_one(
                {"_id": recommendation.id},
                {"$set": document}
            )

        except Exception as e:
            raise DatabaseError(f"Error al actualizar recomendación: {str(e)}")

    async def delete(self, recommendation_id: str) -> None:
        """Eliminar recomendación (soft delete)"""
        try:
            collection = await self._get_collection()
            
            await collection.update_one(
                {"_id": recommendation_id},
                {"$set": {"is_deleted": True}}
            )

        except Exception as e:
            raise DatabaseError(f"Error al eliminar recomendación: {str(e)}")

    async def exists_by_id(self, recommendation_id: str) -> bool:
        """Verificar si existe recomendación por ID"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({"_id": recommendation_id})
            
            return count > 0

        except Exception as e:
            raise DatabaseError(f"Error al verificar existencia: {str(e)}")

    async def count_by_diary_entry_id(self, diary_entry_id: str) -> int:
        """Contar recomendaciones activas por entrada de diario"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "diary_entry_id": diary_entry_id,
                "is_deleted": False
            })
            
            return count

        except Exception as e:
            raise DatabaseError(f"Error al contar recomendaciones: {str(e)}")