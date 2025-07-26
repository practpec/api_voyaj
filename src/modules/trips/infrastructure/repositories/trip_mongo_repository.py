from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ...domain.trip import Trip, TripData
from ...domain.interfaces.trip_repository import ITripRepository
from shared.database.Connection import DatabaseConnection


class TripMongoRepository(ITripRepository):
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self._db = db or DatabaseConnection()
        self._collection = self._db.trips

    async def create(self, trip: Trip) -> Trip:
        trip_data = self._trip_to_document(trip.to_public_data())
        
        result = await self._collection.insert_one(trip_data)
        trip_data["_id"] = result.inserted_id
        
        return self._document_to_trip(trip_data)

    async def find_by_id(self, trip_id: str) -> Optional[Trip]:
        try:
            document = await self._collection.find_one({
                "_id": ObjectId(trip_id),
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_trip(document) if document else None
        except Exception:
            return None

    async def update(self, trip: Trip) -> Trip:
        trip_data = self._trip_to_document(trip.to_public_data())
        trip_data.pop("_id", None)
        
        await self._collection.update_one(
            {"_id": ObjectId(trip.id)},
            {"$set": trip_data}
        )
        
        return trip

    async def delete(self, trip_id: str) -> bool:
        result = await self._collection.update_one(
            {"_id": ObjectId(trip_id)},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    async def find_by_owner_id(
        self, 
        owner_id: str, 
        page: int = 1, 
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Trip], int]:
        query = {
            "owner_id": owner_id,
            "is_deleted": {"$ne": True}
        }
        
        if filters:
            if filters.get("status"):
                query["status"] = filters["status"]
            if filters.get("category"):
                query["category"] = filters["category"]
            if filters.get("is_group_trip") is not None:
                query["is_group_trip"] = filters["is_group_trip"]
            if filters.get("destination"):
                query["destination"] = {"$regex": filters["destination"], "$options": "i"}
            if filters.get("start_date") and filters.get("end_date"):
                query["start_date"] = {
                    "$gte": filters["start_date"],
                    "$lte": filters["end_date"]
                }
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        trips = [self._document_to_trip(doc) for doc in documents]
        return trips, total

    async def find_active_by_owner_id(self, owner_id: str) -> List[Trip]:
        query = {
            "owner_id": owner_id,
            "is_deleted": {"$ne": True},
            "status": {"$in": ["planning", "active"]}
        }
        
        cursor = self._collection.find(query).sort("start_date", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_trip(doc) for doc in documents]

    async def find_by_destination(
        self, 
        destination: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        query = {
            "destination": {"$regex": destination, "$options": "i"},
            "is_deleted": {"$ne": True}
        }
        
        if user_id:
            query["owner_id"] = user_id
        
        cursor = self._collection.find(query).sort("start_date", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_trip(doc) for doc in documents]

    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        query = {
            "$or": [
                {"start_date": {"$gte": start_date, "$lte": end_date}},
                {"end_date": {"$gte": start_date, "$lte": end_date}},
                {"start_date": {"$lte": start_date}, "end_date": {"$gte": end_date}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        if user_id:
            query["owner_id"] = user_id
        
        cursor = self._collection.find(query).sort("start_date", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_trip(doc) for doc in documents]

    async def find_by_category(
        self, 
        category: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        query = {
            "category": category,
            "is_deleted": {"$ne": True}
        }
        
        if user_id:
            query["owner_id"] = user_id
        
        cursor = self._collection.find(query).sort("start_date", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_trip(doc) for doc in documents]

    async def find_group_trips_by_user(self, user_id: str) -> List[Trip]:
        query = {
            "owner_id": user_id,
            "is_group_trip": True,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("start_date", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_trip(doc) for doc in documents]

    async def search(
        self, 
        query: str, 
        user_id: Optional[str] = None
    ) -> List[Trip]:
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"destination": {"$regex": query, "$options": "i"}},
                {"notes": {"$regex": query, "$options": "i"}}
            ],
            "is_deleted": {"$ne": True}
        }
        
        if user_id:
            search_query["owner_id"] = user_id
        
        cursor = self._collection.find(search_query).sort("start_date", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_trip(doc) for doc in documents]

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Trip], int]:
        query = {"is_deleted": {"$ne": True}}
        
        for key, value in filters.items():
            if value is not None:
                if key == "destination":
                    query[key] = {"$regex": value, "$options": "i"}
                elif key == "start_date":
                    query[key] = {"$gte": value}
                elif key == "end_date":
                    query[key] = {"$lte": value}
                else:
                    query[key] = value
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        trips = [self._document_to_trip(doc) for doc in documents]
        return trips, total

    async def count_by_filters(self, filters: Dict[str, Any]) -> int:
        query = {"is_deleted": {"$ne": True}}
        
        for key, value in filters.items():
            if value is not None:
                if key == "destination":
                    query[key] = {"$regex": value, "$options": "i"}
                else:
                    query[key] = value
        
        return await self._collection.count_documents(query)

    async def exists_by_id(self, trip_id: str) -> bool:
        try:
            count = await self._collection.count_documents({
                "_id": ObjectId(trip_id),
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception:
            return False

    async def is_owner(self, trip_id: str, user_id: str) -> bool:
        try:
            count = await self._collection.count_documents({
                "_id": ObjectId(trip_id),
                "owner_id": user_id,
                "is_deleted": {"$ne": True}
            })
            return count > 0
        except Exception:
            return False

    async def get_user_trip_stats(self, user_id: str) -> Dict[str, Any]:
        pipeline = [
            {
                "$match": {
                    "owner_id": user_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_trips": {"$sum": 1},
                    "completed_trips": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    },
                    "active_trips": {
                        "$sum": {"$cond": [{"$eq": ["$status", "active"]}, 1, 0]}
                    },
                    "total_expenses": {"$sum": "$total_expenses"},
                    "destinations": {"$addToSet": "$destination"},
                    "categories": {"$push": "$category"},
                    "avg_duration": {
                        "$avg": {
                            "$divide": [
                                {"$subtract": ["$end_date", "$start_date"]},
                                86400000
                            ]
                        }
                    }
                }
            }
        ]
        
        result = await self._collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_trips": 0,
                "completed_trips": 0,
                "active_trips": 0,
                "total_expenses": 0.0,
                "average_trip_duration": 0.0
            }
        
        stats = result[0]
        return {
            "total_trips": stats.get("total_trips", 0),
            "completed_trips": stats.get("completed_trips", 0),
            "active_trips": stats.get("active_trips", 0),
            "total_expenses": stats.get("total_expenses", 0.0),
            "average_trip_duration": stats.get("avg_duration", 0.0)
        }

    def _trip_to_document(self, trip_data: TripData) -> Dict[str, Any]:
        doc = {
            "_id": ObjectId(trip_data.id),
            "title": trip_data.title,
            "description": trip_data.description,
            "destination": trip_data.destination,
            "start_date": trip_data.start_date,
            "end_date": trip_data.end_date,
            "owner_id": trip_data.owner_id,
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
            "created_at": trip_data.created_at,
            "updated_at": trip_data.updated_at,
            "is_deleted": trip_data.is_deleted
        }
        
        return {k: v for k, v in doc.items() if v is not None}

    def _document_to_trip(self, document: Dict[str, Any]) -> Trip:
        trip_data = TripData(
            id=str(document["_id"]),
            title=document["title"],
            description=document.get("description"),
            destination=document["destination"],
            start_date=document["start_date"],
            end_date=document["end_date"],
            owner_id=document["owner_id"],
            category=document["category"],
            status=document["status"],
            is_group_trip=document.get("is_group_trip", False),
            is_public=document.get("is_public", False),
            budget_limit=document.get("budget_limit"),
            currency=document.get("currency", "USD"),
            image_url=document.get("image_url"),
            notes=document.get("notes"),
            total_expenses=document.get("total_expenses", 0.0),
            member_count=document.get("member_count", 1),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
            is_deleted=document.get("is_deleted", False)
        )
        
        return Trip.from_data(trip_data)