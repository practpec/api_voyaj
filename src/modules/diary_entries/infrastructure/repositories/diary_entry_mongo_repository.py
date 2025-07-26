from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ...domain.diary_entry import DiaryEntry, DiaryEntryData
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from shared.database.Connection import DatabaseConnection


class DiaryEntryMongoRepository(IDiaryEntryRepository):
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self._db = db or DatabaseConnection.get_database()
        self._collection = self._db.diary_entries

    async def create(self, diary_entry: DiaryEntry) -> DiaryEntry:
        entry_data = self._entry_to_document(diary_entry.to_public_data())
        
        result = await self._collection.insert_one(entry_data)
        entry_data["_id"] = result.inserted_id
        
        return self._document_to_entry(entry_data)

    async def find_by_id(self, entry_id: str) -> Optional[DiaryEntry]:
        try:
            document = await self._collection.find_one({
                "_id": ObjectId(entry_id),
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_entry(document) if document else None
        except Exception:
            return None

    async def update(self, diary_entry: DiaryEntry) -> DiaryEntry:
        entry_data = self._entry_to_document(diary_entry.to_public_data())
        entry_data.pop("_id", None)
        
        await self._collection.update_one(
            {"_id": ObjectId(diary_entry.id)},
            {"$set": entry_data}
        )
        
        return diary_entry

    async def delete(self, entry_id: str) -> bool:
        result = await self._collection.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    async def find_by_day_id(self, day_id: str) -> List[DiaryEntry]:
        query = {
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("created_at", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_entry(doc) for doc in documents]

    async def find_by_user_id(self, user_id: str) -> List[DiaryEntry]:
        query = {
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("created_at", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_entry(doc) for doc in documents]

    async def find_by_trip_id(self, trip_id: str) -> List[DiaryEntry]:
        # Necesitamos hacer lookup con días para obtener entradas por trip_id
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "_id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "day.trip_id": trip_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$sort": {"created_at": -1}
            }
        ]
        
        cursor = self._collection.aggregate(pipeline)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_entry(doc) for doc in documents]

    async def find_by_user_and_day(self, user_id: str, day_id: str) -> Optional[DiaryEntry]:
        document = await self._collection.find_one({
            "user_id": user_id,
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        })
        
        return self._document_to_entry(document) if document else None

    async def count_by_day_id(self, day_id: str) -> int:
        return await self._collection.count_documents({
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        })

    async def count_by_user_id(self, user_id: str) -> int:
        return await self._collection.count_documents({
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        })

    async def count_by_trip_id(self, trip_id: str) -> int:
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "_id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "day.trip_id": trip_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$count": "total"
            }
        ]
        
        result = await self._collection.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0

    async def get_user_diary_statistics(self, user_id: str) -> Dict[str, Any]:
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_entries": {"$sum": 1},
                    "entries_with_emotions": {
                        "$sum": {"$cond": [{"$ne": ["$emotions", None]}, 1, 0]}
                    },
                    "all_emotions": {"$push": "$emotions.emotions"}
                }
            }
        ]
        
        result = await self._collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_entries": 0,
                "entries_with_emotions": 0,
                "emotion_distribution": {},
                "most_common_emotion": None
            }
        
        stats = result[0]
        
        # Procesar distribución de emociones
        emotion_counts = {}
        for emotion_list in stats.get("all_emotions", []):
            if emotion_list:
                for emotion in emotion_list:
                    if emotion and "type" in emotion:
                        emotion_type = emotion["type"]
                        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
        
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        
        return {
            "total_entries": stats.get("total_entries", 0),
            "entries_with_emotions": stats.get("entries_with_emotions", 0),
            "emotion_distribution": emotion_counts,
            "most_common_emotion": most_common_emotion
        }

    async def get_trip_diary_statistics(self, trip_id: str) -> Dict[str, Any]:
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "_id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "day.trip_id": trip_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_entries": {"$sum": 1},
                    "entries_with_emotions": {
                        "$sum": {"$cond": [{"$ne": ["$emotions", None]}, 1, 0]}
                    },
                    "contributors": {"$addToSet": "$user_id"},
                    "all_emotions": {"$push": "$emotions.emotions"}
                }
            }
        ]
        
        result = await self._collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_entries": 0,
                "entries_with_emotions": 0,
                "active_contributors": 0,
                "emotion_distribution": {},
                "most_common_emotion": None
            }
        
        stats = result[0]
        
        # Procesar distribución de emociones
        emotion_counts = {}
        for emotion_list in stats.get("all_emotions", []):
            if emotion_list:
                for emotion in emotion_list:
                    if emotion and "type" in emotion:
                        emotion_type = emotion["type"]
                        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1
        
        most_common_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else None
        
        return {
            "total_entries": stats.get("total_entries", 0),
            "entries_with_emotions": stats.get("entries_with_emotions", 0),
            "active_contributors": len(stats.get("contributors", [])),
            "emotion_distribution": emotion_counts,
            "most_common_emotion": most_common_emotion
        }

    async def find_entries_with_emotions(self, trip_id: str) -> List[DiaryEntry]:
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "_id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "day.trip_id": trip_id,
                    "is_deleted": {"$ne": True},
                    "emotions": {"$ne": None, "$exists": True}
                }
            },
            {
                "$sort": {"created_at": -1}
            }
        ]
        
        cursor = self._collection.aggregate(pipeline)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_entry(doc) for doc in documents]

    async def find_entries_by_emotion_type(self, emotion_type: str, trip_id: Optional[str] = None) -> List[DiaryEntry]:
        match_query = {
            "is_deleted": {"$ne": True},
            "emotions.emotions.type": emotion_type
        }
        
        if trip_id:
            pipeline = [
                {
                    "$lookup": {
                        "from": "days",
                        "localField": "day_id",
                        "foreignField": "_id",
                        "as": "day"
                    }
                },
                {
                    "$match": {
                        **match_query,
                        "day.trip_id": trip_id
                    }
                },
                {
                    "$sort": {"created_at": -1}
                }
            ]
            
            cursor = self._collection.aggregate(pipeline)
        else:
            cursor = self._collection.find(match_query).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._document_to_entry(doc) for doc in documents]

    async def search_entries(
        self, 
        query: str, 
        user_id: Optional[str] = None,
        trip_id: Optional[str] = None,
        day_id: Optional[str] = None
    ) -> List[DiaryEntry]:
        search_query = {
            "content": {"$regex": query, "$options": "i"},
            "is_deleted": {"$ne": True}
        }
        
        if user_id:
            search_query["user_id"] = user_id
        
        if day_id:
            search_query["day_id"] = day_id
        
        if trip_id and not day_id:
            pipeline = [
                {
                    "$lookup": {
                        "from": "days",
                        "localField": "day_id",
                        "foreignField": "_id",
                        "as": "day"
                    }
                },
                {
                    "$match": {
                        **search_query,
                        "day.trip_id": trip_id
                    }
                },
                {
                    "$sort": {"created_at": -1}
                }
            ]
            
            cursor = self._collection.aggregate(pipeline)
        else:
            cursor = self._collection.find(search_query).sort("created_at", -1)
        
        documents = await cursor.to_list(length=None)
        return [self._document_to_entry(doc) for doc in documents]

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[DiaryEntry], int]:
        query = {"is_deleted": {"$ne": True}}
        
        if filters.get("user_id"):
            query["user_id"] = filters["user_id"]
        
        if filters.get("day_id"):
            query["day_id"] = filters["day_id"]
        
        if filters.get("has_emotions") is True:
            query["emotions"] = {"$ne": None, "$exists": True}
        elif filters.get("has_emotions") is False:
            query["$or"] = [
                {"emotions": {"$exists": False}},
                {"emotions": None}
            ]
        
        if filters.get("emotion_type"):
            query["emotions.emotions.type"] = filters["emotion_type"]
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        entries = [self._document_to_entry(doc) for doc in documents]
        return entries, total

    async def delete_by_day_id(self, day_id: str) -> bool:
        result = await self._collection.update_many(
            {"day_id": day_id},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    async def delete_by_trip_id(self, trip_id: str) -> bool:
        pipeline_match = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "_id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "day.trip_id": trip_id
                }
            }
        ]
        
        cursor = self._collection.aggregate(pipeline_match)
        entries = await cursor.to_list(length=None)
        
        entry_ids = [ObjectId(entry["_id"]) for entry in entries]
        
        if entry_ids:
            result = await self._collection.update_many(
                {"_id": {"$in": entry_ids}},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        
        return False

    async def get_most_active_days(self, trip_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "_id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "day.trip_id": trip_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$group": {
                    "_id": "$day_id",
                    "entry_count": {"$sum": 1},
                    "day_info": {"$first": "$day"}
                }
            },
            {
                "$sort": {"entry_count": -1}
            },
            {
                "$limit": limit
            }
        ]
        
        cursor = self._collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        return [{
            "day_id": str(result["_id"]),
            "entry_count": result["entry_count"],
            "day_date": result["day_info"][0]["date"] if result["day_info"] else None
        } for result in results]

    async def get_emotion_trends(self, trip_id: str) -> Dict[str, Any]:
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "_id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "day.trip_id": trip_id,
                    "is_deleted": {"$ne": True},
                    "emotions": {"$ne": None, "$exists": True}
                }
            },
            {
                "$unwind": "$emotions.emotions"
            },
            {
                "$group": {
                    "_id": {
                        "emotion_type": "$emotions.emotions.type",
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}
                    },
                    "average_intensity": {"$avg": "$emotions.emotions.intensity"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.date": 1}
            }
        ]
        
        cursor = self._collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        # Organizar resultados por tipo de emoción
        trends = {}
        for result in results:
            emotion_type = result["_id"]["emotion_type"]
            date = result["_id"]["date"]
            
            if emotion_type not in trends:
                trends[emotion_type] = []
            
            trends[emotion_type].append({
                "date": date,
                "average_intensity": result["average_intensity"],
                "count": result["count"]
            })
        
        return trends

    def _entry_to_document(self, entry_data: DiaryEntryData) -> Dict[str, Any]:
        """Convertir DiaryEntryData a documento MongoDB"""
        return {
            "day_id": entry_data.day_id,
            "user_id": entry_data.user_id,
            "content": entry_data.content,
            "emotions": entry_data.emotions,
            "is_deleted": entry_data.is_deleted,
            "created_at": entry_data.created_at,
            "updated_at": entry_data.updated_at
        }

    def _document_to_entry(self, document: Dict[str, Any]) -> DiaryEntry:
        """Convertir documento MongoDB a DiaryEntry"""
        data = DiaryEntryData(
            id=str(document["_id"]),
            day_id=document["day_id"],
            user_id=document["user_id"],
            content=document["content"],
            emotions=document.get("emotions"),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        
        return DiaryEntry(data)