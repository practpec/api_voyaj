from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING

from ...domain.activity_vote import ActivityVote
from ...domain.interfaces.activity_vote_repository import IActivityVoteRepository
from shared.database.Connection import DatabaseConnection


class ActivityVoteMongoRepository(IActivityVoteRepository):
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self._db = db or DatabaseConnection.get_database()
        self._collection = self._db.activity_votes

    async def create(self, vote: ActivityVote) -> ActivityVote:
        """Crear nuevo voto"""
        vote_data = vote.to_dict()
        
        await self._collection.insert_one(vote_data)
        return vote

    async def find_by_id(self, vote_id: str) -> Optional[ActivityVote]:
        """Buscar voto por ID"""
        data = await self._collection.find_one({"id": vote_id, "is_deleted": False})
        return ActivityVote.from_dict(data) if data else None

    async def find_by_activity_and_user(self, activity_id: str, user_id: str) -> Optional[ActivityVote]:
        """Buscar voto específico de usuario para una actividad"""
        data = await self._collection.find_one({
            "activity_id": activity_id,
            "user_id": user_id,
            "is_deleted": False
        })
        return ActivityVote.from_dict(data) if data else None

    async def update(self, vote: ActivityVote) -> ActivityVote:
        """Actualizar voto"""
        vote_data = vote.to_dict()
        
        await self._collection.update_one(
            {"id": vote.id},
            {"$set": vote_data}
        )
        return vote

    async def delete(self, vote_id: str) -> bool:
        """Eliminar voto (soft delete)"""
        result = await self._collection.update_one(
            {"id": vote_id},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def find_by_activity_id(self, activity_id: str) -> List[ActivityVote]:
        """Buscar todos los votos de una actividad"""
        cursor = self._collection.find({
            "activity_id": activity_id,
            "is_deleted": False
        }).sort("created_at", ASCENDING)
        
        votes = []
        async for data in cursor:
            votes.append(ActivityVote.from_dict(data))
        return votes

    async def find_by_user_id(self, user_id: str, trip_id: Optional[str] = None) -> List[ActivityVote]:
        """Buscar votos de un usuario"""
        filters = {"user_id": user_id, "is_deleted": False}
        if trip_id:
            filters["trip_id"] = trip_id
            
        cursor = self._collection.find(filters).sort("created_at", DESCENDING)
        
        votes = []
        async for data in cursor:
            votes.append(ActivityVote.from_dict(data))
        return votes

    async def find_by_trip_id(self, trip_id: str) -> List[ActivityVote]:
        """Buscar votos de un viaje"""
        cursor = self._collection.find({
            "trip_id": trip_id,
            "is_deleted": False
        }).sort("created_at", DESCENDING)
        
        votes = []
        async for data in cursor:
            votes.append(ActivityVote.from_dict(data))
        return votes

    async def count_by_activity_id(self, activity_id: str) -> int:
        """Contar votos de una actividad"""
        return await self._collection.count_documents({
            "activity_id": activity_id,
            "is_deleted": False
        })

    async def count_by_vote_type(self, activity_id: str, vote_type: str) -> int:
        """Contar votos por tipo para una actividad"""
        return await self._collection.count_documents({
            "activity_id": activity_id,
            "vote_type": vote_type,
            "is_deleted": False
        })

    async def get_activity_vote_stats(self, activity_id: str) -> Dict[str, int]:
        """Obtener estadísticas de votos para una actividad"""
        pipeline = [
            {"$match": {"activity_id": activity_id, "is_deleted": False}},
            {"$group": {
                "_id": "$vote_type",
                "count": {"$sum": 1}
            }}
        ]
        
        result = {}
        async for doc in self._collection.aggregate(pipeline):
            result[doc["_id"]] = doc["count"]
        
        return {
            "up": result.get("up", 0),
            "down": result.get("down", 0),
            "neutral": result.get("neutral", 0)
        }

    async def get_trip_vote_rankings(self, trip_id: str) -> List[Dict[str, Any]]:
        """Obtener ranking de actividades por votos en un viaje"""
        pipeline = [
            {"$match": {"trip_id": trip_id, "is_deleted": False}},
            {"$group": {
                "_id": "$activity_id",
                "total_votes": {"$sum": 1},
                "up_votes": {
                    "$sum": {"$cond": [{"$eq": ["$vote_type", "up"]}, 1, 0]}
                },
                "down_votes": {
                    "$sum": {"$cond": [{"$eq": ["$vote_type", "down"]}, 1, 0]}
                }
            }},
            {"$addFields": {
                "score": {"$subtract": ["$up_votes", "$down_votes"]},
                "popularity_percentage": {
                    "$cond": [
                        {"$gt": ["$total_votes", 0]},
                        {"$multiply": [{"$divide": ["$up_votes", "$total_votes"]}, 100]},
                        0
                    ]
                }
            }},
            {"$sort": {"score": DESCENDING, "total_votes": DESCENDING}},
            {"$lookup": {
                "from": "activities",
                "localField": "_id",
                "foreignField": "id",
                "as": "activity_info"
            }},
            {"$unwind": "$activity_info"},
            {"$project": {
                "activity_id": "$_id",
                "activity_title": "$activity_info.title",
                "activity_description": "$activity_info.description",
                "total_votes": 1,
                "score": 1,
                "popularity_percentage": {"$round": ["$popularity_percentage", 1]}
            }}
        ]
        
        rankings = []
        position = 1
        async for doc in self._collection.aggregate(pipeline):
            doc["ranking_position"] = position
            rankings.append(doc)
            position += 1
        
        return rankings

    async def get_trip_polls(self, trip_id: str) -> List[Dict[str, Any]]:
        """Obtener encuestas activas de un viaje"""
        pipeline = [
            {"$match": {"trip_id": trip_id, "is_deleted": False}},
            {"$group": {
                "_id": "$activity_id",
                "total_votes": {"$sum": 1},
                "vote_distribution": {
                    "$push": {
                        "user_id": "$user_id",
                        "vote_type": "$vote_type",
                        "created_at": "$created_at"
                    }
                }
            }},
            {"$match": {"total_votes": {"$gte": 1}}},
            {"$lookup": {
                "from": "activities",
                "localField": "_id",
                "foreignField": "id",
                "as": "activity_info"
            }},
            {"$unwind": "$activity_info"},
            {"$project": {
                "activity_id": "$_id",
                "activity_title": "$activity_info.title",
                "total_votes": 1,
                "vote_distribution": 1,
                "is_active": True
            }},
            {"$sort": {"total_votes": DESCENDING}}
        ]
        
        polls = []
        async for doc in self._collection.aggregate(pipeline):
            polls.append(doc)
        
        return polls

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[ActivityVote], int]:
        """Buscar votos con filtros y paginación"""
        query = {"is_deleted": False}
        query.update(filters)
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).skip(skip).limit(limit).sort("created_at", DESCENDING)
        votes = []
        async for data in cursor:
            votes.append(ActivityVote.from_dict(data))
        
        total = await self._collection.count_documents(query)
        return votes, total