from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorCollection
from collections import Counter

from ...domain.diary_entry import DiaryEntry
from ...domain.interfaces.diary_entry_repository import IDiaryEntryRepository
from shared.database.Connection import DatabaseConnection


class DiaryEntryMongoRepository(IDiaryEntryRepository):
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "diary_entries"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        database = self._db_connection.get_database()
        return database[self._collection_name]

    async def create(self, diary_entry: DiaryEntry) -> DiaryEntry:
        collection = await self._get_collection()
        entry_data = diary_entry.to_dict()
        await collection.insert_one(entry_data)
        return diary_entry

    async def find_by_id(self, entry_id: str) -> Optional[DiaryEntry]:
        collection = await self._get_collection()
        entry_data = await collection.find_one({
            "id": entry_id,
            "is_deleted": {"$ne": True}
        })
        
        if entry_data:
            return DiaryEntry.from_dict(entry_data)
        return None

    async def update(self, diary_entry: DiaryEntry) -> DiaryEntry:
        collection = await self._get_collection()
        entry_data = diary_entry.to_dict()
        entry_data["updated_at"] = datetime.utcnow()
        
        await collection.update_one(
            {"id": diary_entry.id},
            {"$set": entry_data}
        )
        return diary_entry

    async def delete(self, entry_id: str) -> bool:
        collection = await self._get_collection()
        result = await collection.update_one(
            {"id": entry_id},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0

    async def find_by_day_id(self, day_id: str) -> List[DiaryEntry]:
        collection = await self._get_collection()
        cursor = collection.find({
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        }).sort("created_at", 1)
        
        entries = []
        async for entry_data in cursor:
            entries.append(DiaryEntry.from_dict(entry_data))
        
        return entries

    async def find_by_user_id(self, user_id: str) -> List[DiaryEntry]:
        collection = await self._get_collection()
        cursor = collection.find({
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }).sort("created_at", -1)
        
        entries = []
        async for entry_data in cursor:
            entries.append(DiaryEntry.from_dict(entry_data))
        
        return entries

    async def find_by_trip_id(self, trip_id: str) -> List[DiaryEntry]:
        collection = await self._get_collection()
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "id",
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
        
        cursor = collection.aggregate(pipeline)
        entries = []
        async for entry_data in cursor:
            entries.append(DiaryEntry.from_dict(entry_data))
        
        return entries

    async def find_by_user_and_day(self, user_id: str, day_id: str) -> Optional[DiaryEntry]:
        collection = await self._get_collection()
        entry_data = await collection.find_one({
            "user_id": user_id,
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        })
        
        if entry_data:
            return DiaryEntry.from_dict(entry_data)
        return None

    async def count_by_day_id(self, day_id: str) -> int:
        collection = await self._get_collection()
        return await collection.count_documents({
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        })

    async def count_by_user_id(self, user_id: str) -> int:
        collection = await self._get_collection()
        return await collection.count_documents({
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        })

    async def count_by_trip_id(self, trip_id: str) -> int:
        collection = await self._get_collection()
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "id",
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
        
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(1)
        return result[0]["total"] if result else 0

    async def count_by_user_and_trip(self, user_id: str, trip_id: str) -> int:
        collection = await self._get_collection()
        pipeline = [
            {
                "$lookup": {
                    "from": "days",
                    "localField": "day_id",
                    "foreignField": "id",
                    "as": "day"
                }
            },
            {
                "$match": {
                    "user_id": user_id,
                    "day.trip_id": trip_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$count": "total"
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(1)
        return result[0]["total"] if result else 0

    async def get_user_diary_statistics(self, user_id: str) -> Dict[str, Any]:
        entries = await self.find_by_user_id(user_id)
        
        if not entries:
            return {
                "total_entries": 0,
                "total_words": 0,
                "average_words_per_entry": 0.0,
                "most_common_emotion": None,
                "entries_with_emotions": 0,
                "emotion_distribution": {}
            }
        
        total_words = sum(len(entry.content.split()) for entry in entries if entry.content)
        all_emotions = []
        entries_with_emotions = 0
        
        for entry in entries:
            if entry.emotions:
                all_emotions.extend(entry.emotions)
                entries_with_emotions += 1
        
        emotion_counter = Counter(all_emotions)
        most_common = emotion_counter.most_common(1)
        
        return {
            "total_entries": len(entries),
            "total_words": total_words,
            "average_words_per_entry": total_words / len(entries) if entries else 0.0,
            "most_common_emotion": most_common[0][0] if most_common else None,
            "entries_with_emotions": entries_with_emotions,
            "emotion_distribution": dict(emotion_counter)
        }

    async def get_trip_diary_statistics(self, trip_id: str) -> Dict[str, Any]:
        entries = await self.find_by_trip_id(trip_id)
        
        if not entries:
            return {
                "total_entries": 0,
                "total_words": 0,
                "average_words_per_entry": 0.0,
                "most_common_emotion": None,
                "entries_with_emotions": 0,
                "entries_by_day": {},
                "emotion_distribution": {}
            }
        
        total_words = sum(len(entry.content.split()) for entry in entries if entry.content)
        all_emotions = []
        entries_with_emotions = 0
        entries_by_day = {}
        
        for entry in entries:
            if entry.emotions:
                all_emotions.extend(entry.emotions)
                entries_with_emotions += 1
            
            day_key = entry.day_id
            entries_by_day[day_key] = entries_by_day.get(day_key, 0) + 1
        
        emotion_counter = Counter(all_emotions)
        most_common = emotion_counter.most_common(1)
        
        return {
            "total_entries": len(entries),
            "total_words": total_words,
            "average_words_per_entry": total_words / len(entries) if entries else 0.0,
            "most_common_emotion": most_common[0][0] if most_common else None,
            "entries_with_emotions": entries_with_emotions,
            "entries_by_day": entries_by_day,
            "emotion_distribution": dict(emotion_counter)
        }

    async def find_entries_with_emotions(self, trip_id: str) -> List[DiaryEntry]:
        entries = await self.find_by_trip_id(trip_id)
        return [entry for entry in entries if entry.emotions]

    async def find_entries_by_emotion_type(self, emotion_type: str, trip_id: Optional[str] = None) -> List[DiaryEntry]:
        collection = await self._get_collection()
        query = {
            "emotions": emotion_type.lower(),
            "is_deleted": {"$ne": True}
        }
        
        if trip_id:
            pipeline = [
                {
                    "$lookup": {
                        "from": "days",
                        "localField": "day_id",
                        "foreignField": "id",
                        "as": "day"
                    }
                },
                {
                    "$match": {
                        **query,
                        "day.trip_id": trip_id
                    }
                },
                {
                    "$sort": {"created_at": -1}
                }
            ]
            
            cursor = collection.aggregate(pipeline)
            entries = []
            async for entry_data in cursor:
                entries.append(DiaryEntry.from_dict(entry_data))
            return entries
        else:
            cursor = collection.find(query).sort("created_at", -1)
            entries = []
            async for entry_data in cursor:
                entries.append(DiaryEntry.from_dict(entry_data))
            return entries

    async def get_most_active_writers(self, trip_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        entries = await self.find_by_trip_id(trip_id)
        user_stats = {}
        
        for entry in entries:
            user_id = entry.user_id
            if user_id not in user_stats:
                user_stats[user_id] = {
                    "_id": user_id,
                    "entries_count": 0,
                    "total_words": 0
                }
            
            user_stats[user_id]["entries_count"] += 1
            if entry.content:
                user_stats[user_id]["total_words"] += len(entry.content.split())
        
        sorted_users = sorted(
            user_stats.values(),
            key=lambda x: x["entries_count"],
            reverse=True
        )
        
        return sorted_users[:limit]

    async def get_emotion_trends_by_trip(self, trip_id: str) -> Dict[str, Any]:
        entries = await self.find_by_trip_id(trip_id)
        emotion_counts = Counter()
        
        for entry in entries:
            if entry.emotions:
                for emotion in entry.emotions:
                    emotion_counts[emotion] += 1
        
        trends = [
            {
                "_id": emotion,
                "total": count,
                "timeline": []
            }
            for emotion, count in emotion_counts.most_common()
        ]
        
        return {
            "trends": trends,
            "total_emotions": sum(emotion_counts.values())
        }

    async def find_entries_by_date_range(
        self,
        trip_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[DiaryEntry]:
        entries = await self.find_by_trip_id(trip_id)
        
        if start_date or end_date:
            filtered_entries = []
            for entry in entries:
                entry_date = entry.created_at
                
                if start_date and entry_date < datetime.fromisoformat(start_date):
                    continue
                if end_date and entry_date > datetime.fromisoformat(end_date):
                    continue
                
                filtered_entries.append(entry)
            
            return filtered_entries
        
        return entries