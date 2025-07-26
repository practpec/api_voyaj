from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ...domain.activity import Activity, ActivityData, ActivityStatus
from ...domain.interfaces.activity_repository import IActivityRepository
from shared.database.Connection import DatabaseConnection


class ActivityMongoRepository(IActivityRepository):
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self._db = db or DatabaseConnection.get_database()
        self._collection = self._db.activities

    async def create(self, activity: Activity) -> Activity:
        activity_data = self._activity_to_document(activity.to_public_data())
        
        result = await self._collection.insert_one(activity_data)
        activity_data["_id"] = result.inserted_id
        
        return self._document_to_activity(activity_data)

    async def find_by_id(self, activity_id: str) -> Optional[Activity]:
        try:
            document = await self._collection.find_one({
                "_id": ObjectId(activity_id),
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_activity(document) if document else None
        except Exception:
            return None

    async def update(self, activity: Activity) -> Activity:
        activity_data = self._activity_to_document(activity.to_public_data())
        activity_data.pop("_id", None)
        
        await self._collection.update_one(
            {"_id": ObjectId(activity.id)},
            {"$set": activity_data}
        )
        
        return activity

    async def delete(self, activity_id: str) -> bool:
        result = await self._collection.update_one(
            {"_id": ObjectId(activity_id)},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        
        return result.modified_count > 0

    async def find_by_day_id(self, day_id: str) -> List[Activity]:
        query = {
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("order", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_activity(doc) for doc in documents]

    async def find_by_day_id_ordered(self, day_id: str) -> List[Activity]:
        query = {
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort([("order", 1), ("start_time", 1)])
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_activity(doc) for doc in documents]

    async def find_by_trip_id(self, trip_id: str) -> List[Activity]:
        # Para obtener actividades por trip_id, necesitamos hacer lookup con días
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
                "$sort": {"day.date": 1, "order": 1}
            }
        ]
        
        cursor = self._collection.aggregate(pipeline)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_activity(doc) for doc in documents]

    async def find_by_status(self, day_id: str, status: str) -> List[Activity]:
        query = {
            "day_id": day_id,
            "status": status,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("order", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_activity(doc) for doc in documents]

    async def find_by_category(self, day_id: str, category: str) -> List[Activity]:
        query = {
            "day_id": day_id,
            "category": category,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("order", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_activity(doc) for doc in documents]

    async def find_by_user(self, user_id: str, trip_id: Optional[str] = None) -> List[Activity]:
        match_query = {
            "created_by": user_id,
            "is_deleted": {"$ne": True}
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
        return [self._document_to_activity(doc) for doc in documents]

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Activity], int]:
        query = {"is_deleted": {"$ne": True}}
        
        if filters.get("day_id"):
            query["day_id"] = filters["day_id"]
        
        if filters.get("status"):
            query["status"] = filters["status"]
        
        if filters.get("category"):
            query["category"] = filters["category"]
        
        if filters.get("created_by"):
            query["created_by"] = filters["created_by"]
        
        if filters.get("has_cost") is True:
            query["$or"] = [
                {"estimated_cost": {"$exists": True, "$ne": None}},
                {"actual_cost": {"$exists": True, "$ne": None}}
            ]
        elif filters.get("has_cost") is False:
            query["$and"] = [
                {"estimated_cost": {"$in": [None, 0]}},
                {"actual_cost": {"$in": [None, 0]}}
            ]
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("order", 1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        activities = [self._document_to_activity(doc) for doc in documents]
        return activities, total

    async def count_by_day_id(self, day_id: str) -> int:
        return await self._collection.count_documents({
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        })

    async def count_by_status(self, day_id: str, status: str) -> int:
        return await self._collection.count_documents({
            "day_id": day_id,
            "status": status,
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

    async def get_next_order(self, day_id: str) -> int:
        result = await self._collection.find({
            "day_id": day_id,
            "is_deleted": {"$ne": True}
        }).sort("order", -1).limit(1).to_list(length=1)
        
        if result:
            return result[0]["order"] + 1
        return 1

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
        activities = await cursor.to_list(length=None)
        
        activity_ids = [ObjectId(act["_id"]) for act in activities]
        
        if activity_ids:
            result = await self._collection.update_many(
                {"_id": {"$in": activity_ids}},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        
        return False

    async def bulk_update_order(self, activity_orders: List[Dict[str, Any]]) -> bool:
        operations = []
        
        for item in activity_orders:
            operations.append({
                "updateOne": {
                    "filter": {"_id": ObjectId(item["activity_id"])},
                    "update": {
                        "$set": {
                            "order": item["order"],
                            "updated_at": datetime.utcnow()
                        }
                    }
                }
            })
        
        if operations:
            result = await self._collection.bulk_write(operations)
            return result.modified_count > 0
        
        return False

    async def get_day_activity_statistics(self, day_id: str) -> Dict[str, Any]:
        pipeline = [
            {
                "$match": {
                    "day_id": day_id,
                    "is_deleted": {"$ne": True}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_activities": {"$sum": 1},
                    "completed_activities": {
                        "$sum": {"$cond": [{"$eq": ["$status", ActivityStatus.COMPLETED.value]}, 1, 0]}
                    },
                    "in_progress_activities": {
                        "$sum": {"$cond": [{"$eq": ["$status", ActivityStatus.IN_PROGRESS.value]}, 1, 0]}
                    },
                    "planned_activities": {
                        "$sum": {"$cond": [{"$eq": ["$status", ActivityStatus.PLANNED.value]}, 1, 0]}
                    },
                    "cancelled_activities": {
                        "$sum": {"$cond": [{"$eq": ["$status", ActivityStatus.CANCELLED.value]}, 1, 0]}
                    },
                    "total_estimated_cost": {
                        "$sum": {"$ifNull": ["$estimated_cost", 0]}
                    },
                    "total_actual_cost": {
                        "$sum": {"$ifNull": ["$actual_cost", 0]}
                    }
                }
            }
        ]
        
        result = await self._collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_activities": 0,
                "completed_activities": 0,
                "in_progress_activities": 0,
                "planned_activities": 0,
                "cancelled_activities": 0,
                "completion_percentage": 0.0,
                "total_estimated_cost": 0.0,
                "total_actual_cost": 0.0
            }
        
        stats = result[0]
        total = stats.get("total_activities", 0)
        completed = stats.get("completed_activities", 0)
        
        return {
            **stats,
            "completion_percentage": (completed / total * 100) if total > 0 else 0.0
        }

    async def get_trip_activity_statistics(self, trip_id: str) -> Dict[str, Any]:
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
                    "total_activities": {"$sum": 1},
                    "completed_activities": {
                        "$sum": {"$cond": [{"$eq": ["$status", ActivityStatus.COMPLETED.value]}, 1, 0]}
                    },
                    "activities_by_category": {"$push": "$category"}
                }
            }
        ]
        
        result = await self._collection.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_activities": 0,
                "completed_activities": 0,
                "completion_percentage": 0.0,
                "activities_by_category": {}
            }
        
        stats = result[0]
        total = stats.get("total_activities", 0)
        completed = stats.get("completed_activities", 0)
        
        # Contar categorías
        categories = {}
        for category in stats.get("activities_by_category", []):
            categories[category] = categories.get(category, 0) + 1
        
        return {
            "total_activities": total,
            "completed_activities": completed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0.0,
            "activities_by_category": categories
        }

    async def search_activities(
        self, 
        query: str, 
        trip_id: Optional[str] = None,
        day_id: Optional[str] = None
    ) -> List[Activity]:
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}}
            ],
            "is_deleted": {"$ne": True}
        }
        
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
                    "$sort": {"order": 1}
                }
            ]
            
            cursor = self._collection.aggregate(pipeline)
        else:
            cursor = self._collection.find(search_query).sort("order", 1)
        
        documents = await cursor.to_list(length=None)
        return [self._document_to_activity(doc) for doc in documents]

    def _activity_to_document(self, activity_data: ActivityData) -> Dict[str, Any]:
        doc = {
            "_id": ObjectId(activity_data.id),
            "day_id": activity_data.day_id,
            "title": activity_data.title,
            "description": activity_data.description,
            "location": activity_data.location,
            "start_time": activity_data.start_time,
            "end_time": activity_data.end_time,
            "estimated_cost": activity_data.estimated_cost,
            "actual_cost": activity_data.actual_cost,
            "category": activity_data.category,
            "status": activity_data.status,
            "order": activity_data.order,
            "created_by": activity_data.created_by,
            "is_deleted": activity_data.is_deleted,
            "created_at": activity_data.created_at,
            "updated_at": activity_data.updated_at
        }
        
        return {k: v for k, v in doc.items() if v is not None}

    def _document_to_activity(self, document: Dict[str, Any]) -> Activity:
        activity_data = ActivityData(
            id=str(document["_id"]),
            day_id=document["day_id"],
            title=document["title"],
            description=document.get("description"),
            location=document.get("location"),
            start_time=document.get("start_time"),
            end_time=document.get("end_time"),
            estimated_cost=document.get("estimated_cost"),
            actual_cost=document.get("actual_cost"),
            category=document["category"],
            status=document["status"],
            order=document["order"],
            created_by=document["created_by"],
            is_deleted=document.get("is_deleted", False),
            created_at=document["created_at"],
            updated_at=document["updated_at"]
        )
        
        return Activity.from_data(activity_data)