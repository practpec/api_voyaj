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
        day_data = self._day_to_document(day.to_public_data())
        
        result = await self._collection.insert_one(day_data)
        day_data["_id"] = result.inserted_id
        
        return self._document_to_day(day_data)

    async def find_by_id(self, day_id: str) -> Optional[Day]:
        try:
            document = await self._collection.find_one({
                "_id": ObjectId(day_id),
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_day(document) if document else None
        except Exception:
            return None

    async def update(self, day: Day) -> Day:
        day_data = self._day_to_document(day.to_public_data())
        day_data.pop("_id", None)
        
        await self._collection.update_one(
            {"_id": ObjectId(day.id)},
            {"$set": day_data}
        )
        
        return day

    async def delete(self, day_id: str) -> bool:
        result = await self._collection.update_one(
            {"_id": ObjectId(day_id)},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    async def find_by_trip_id(self, trip_id: str) -> List[Day]:
        query = {
            "trip_id": trip_id,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("date", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_day(doc) for doc in documents]

    async def find_by_trip_id_ordered(self, trip_id: str) -> List[Day]:
        query = {
            "trip_id": trip_id,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("date", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_day(doc) for doc in documents]

    async def find_by_trip_and_date(self, trip_id: str, day_date: date) -> Optional[Day]:
        document = await self._collection.find_one({
            "trip_id": trip_id,
            "date": day_date,
            "is_deleted": {"$ne": True}
        })
        
        return self._document_to_day(document) if document else None

    async def find_by_date_range(
        self, 
        trip_id: str, 
        start_date: date, 
        end_date: date
    ) -> List[Day]:
        query = {
            "trip_id": trip_id,
            "date": {"$gte": start_date, "$lte": end_date},
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("date", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_day(doc) for doc in documents]

    async def find_with_notes(self, trip_id: str) -> List[Day]:
        query = {
            "trip_id": trip_id,
            "notes": {"$exists": True, "$ne": None, "$ne": ""},
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("date", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_day(doc) for doc in documents]

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Day], int]:
        query = {"is_deleted": {"$ne": True}}
        
        if filters.get("trip_id"):
            query["trip_id"] = filters["trip_id"]
        
        if filters.get("start_date") and filters.get("end_date"):
            query["date"] = {
                "$gte": filters["start_date"],
                "$lte": filters["end_date"]
            }
        
        if filters.get("has_notes") is True:
            query["notes"] = {"$exists": True, "$ne": None, "$ne": ""}
        elif filters.get("has_notes") is False:
            query["$or"] = [
                {"notes": {"$exists": False}},
                {"notes": None},
                {"notes": ""}
            ]
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("date", 1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        days = [self._document_to_day(doc) for doc in documents]
        return days, total

    async def count_by_trip_id(self, trip_id: str) -> int:
        return await self._collection.count_documents({
            "trip_id": trip_id,
            "is_deleted": {"$ne": True}
        })

    async def count_with_notes(self, trip_id: str) -> int:
        return await self._collection.count_documents({
            "trip_id": trip_id,
            "notes": {"$exists": True, "$ne": None, "$ne": ""},
            "is_deleted": {"$ne": True}
        })

    async def exists_by_trip_and_date(self, trip_id: str, day_date: date) -> bool:
        count = await self._collection.count_documents({
            "trip_id": trip_id,
            "date": day_date,
            "is_deleted": {"$ne": True}
        })
        
        return count > 0

    async def delete_by_trip_id(self, trip_id: str) -> bool:
        result = await self._collection.update_many(
            {"trip_id": trip_id},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    async def bulk_create(self, days: List[Day]) -> List[Day]:
        if not days:
            return []
        
        documents = [self._day_to_document(day.to_public_data()) for day in days]
        
        result = await self._collection.insert_many(documents)
        
        created_days = []
        for i, day in enumerate(days):
            documents[i]["_id"] = result.inserted_ids[i]
            created_days.append(self._document_to_day(documents[i]))
        
        return created_days

    async def get_trip_day_statistics(self, trip_id: str) -> Dict[str, Any]:
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

    def _day_to_document(self, day_data: DayData) -> Dict[str, Any]:
        doc = {
            "_id": ObjectId(day_data.id),
            "trip_id": day_data.trip_id,
            "date": day_data.date,
            "notes": day_data.notes,
            "is_deleted": day_data.is_deleted,
            "created_at": day_data.created_at,
            "updated_at": day_data.updated_at
        }
        
        return {k: v for k, v in doc.items() if v is not None}

    def _document_to_day(self, document: Dict[str, Any]) -> Day:
        day_data = DayData(
            id=str(document["_id"]),
            trip_id=document["trip_id"],
            date=document["date"],
            notes=document.get("notes"),
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        
        return Day.from_data(day_data)