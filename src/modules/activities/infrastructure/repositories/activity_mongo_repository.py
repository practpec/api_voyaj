# src/modules/activities/infrastructure/repositories/activity_mongo_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

from ...domain.activity import Activity, ActivityData, ActivityStatus
from ...domain.interfaces.activity_repository import IActivityRepository
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class ActivityMongoRepository(IActivityRepository):
    """
    MongoDB implementation of the activity repository.
    It handles all database operations related to activities.
    """
    def __init__(self):
        """Initializes the repository by setting up the database connection."""
        self._db_connection = DatabaseConnection()
        self._collection_name = "activities"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Gets the activities collection from the database."""
        database: AsyncIOMotorDatabase = self._db_connection.get_database()
        return database[self._collection_name]

    # region CRUD Methods
    async def create(self, activity: Activity) -> Activity:
        """Creates a new activity in the database."""
        try:
            collection = await self._get_collection()
            activity_doc = self._activity_to_document(activity.to_public_data())
            
            # ✅ CORREGIDO: No generar ObjectId, usar el ID del dominio
            await collection.insert_one(activity_doc)
            return activity
        except Exception as e:
            raise DatabaseError(f"Error creating activity: {str(e)}")

    async def find_by_id(self, activity_id: str) -> Optional[Activity]:
        """Finds an activity by its ID."""
        try:
            collection = await self._get_collection()
            # ✅ CORREGIDO: Usar string ID directamente
            document = await collection.find_one({
                "_id": activity_id,
                "is_deleted": {"$ne": True}
            })
            return self._document_to_activity(document) if document else None
        except Exception as e:
            print(f"[ERROR] Error finding activity by ID: {str(e)}")
            return None

    async def update(self, activity: Activity) -> Activity:
        """Updates an existing activity."""
        try:
            collection = await self._get_collection()
            activity_data = self._activity_to_document(activity.to_public_data())
            activity_data.pop("_id", None)
            activity_data["updated_at"] = datetime.utcnow()

            # ✅ CORREGIDO: Usar string ID directamente
            await collection.update_one(
                {"_id": activity.id},
                {"$set": activity_data}
            )
            return activity
        except Exception as e:
            raise DatabaseError(f"Error updating activity: {str(e)}")

    async def delete(self, activity_id: str) -> bool:
        """Performs a soft delete on a single activity."""
        try:
            collection = await self._get_collection()
            # ✅ CORREGIDO: Usar string ID directamente
            result = await collection.update_one(
                {"_id": activity_id},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting activity: {str(e)}")
    # endregion

    # region Find Methods
    async def find_by_day_id(self, day_id: str) -> List[Activity]:
        """Finds all activities for a specific day, sorted by order."""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "day_id": day_id,
                "is_deleted": {"$ne": True}
            }).sort("order", 1)
            documents = await cursor.to_list(length=None)
            return [self._document_to_activity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error finding activities by day ID: {str(e)}")

    async def find_by_day_id_ordered(self, day_id: str) -> List[Activity]:
        """Finds activities for a day, sorted by order and start time."""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "day_id": day_id,
                "is_deleted": {"$ne": True}
            }).sort([("order", 1), ("start_time", 1)])
            documents = await cursor.to_list(length=None)
            return [self._document_to_activity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error finding ordered activities by day ID: {str(e)}")

    async def find_by_trip_id(self, trip_id: str) -> List[Activity]:
        """Finds all activities for a specific trip through day lookup."""
        try:
            collection = await self._get_collection()
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
                {"$sort": {"day.date": 1, "order": 1}}
            ]
            cursor = collection.aggregate(pipeline)
            documents = await cursor.to_list(length=None)
            return [self._document_to_activity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error finding activities by trip ID: {str(e)}")

    async def find_by_status(self, day_id: str, status: str) -> List[Activity]:
        """Finds activities by status for a specific day."""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "day_id": day_id,
                "status": status,
                "is_deleted": {"$ne": True}
            }).sort("order", 1)
            documents = await cursor.to_list(length=None)
            return [self._document_to_activity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error finding activities by status: {str(e)}")

    async def find_by_category(self, day_id: str, category: str) -> List[Activity]:
        """Finds activities by category for a specific day."""
        try:
            collection = await self._get_collection()
            cursor = collection.find({
                "day_id": day_id,
                "category": category,
                "is_deleted": {"$ne": True}
            }).sort("order", 1)
            documents = await cursor.to_list(length=None)
            return [self._document_to_activity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error finding activities by category: {str(e)}")

    async def find_by_user(self, user_id: str, trip_id: Optional[str] = None) -> List[Activity]:
        """Finds activities created by a specific user."""
        try:
            collection = await self._get_collection()
            query = {
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
                            **query,
                            "day.trip_id": trip_id
                        }
                    },
                    {"$sort": {"created_at": -1}}
                ]
                cursor = collection.aggregate(pipeline)
            else:
                cursor = collection.find(query).sort("created_at", -1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_activity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error finding activities by user: {str(e)}")

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Activity], int]:
        """Finds activities with filters and pagination."""
        try:
            collection = await self._get_collection()
            query = {"is_deleted": {"$ne": True}}
            query.update(filters)
            
            skip = (page - 1) * limit
            cursor = collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            total = await collection.count_documents(query)
            
            activities = [self._document_to_activity(doc) for doc in documents]
            return activities, total
        except Exception as e:
            raise DatabaseError(f"Error finding activities with filters: {str(e)}")

    async def search_activities(
        self, 
        query: str, 
        day_id: Optional[str] = None, 
        trip_id: Optional[str] = None
    ) -> List[Activity]:
        """Searches activities by text in title, description, and location."""
        try:
            collection = await self._get_collection()
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
                    {"$sort": {"order": 1}}
                ]
                cursor = collection.aggregate(pipeline)
            else:
                cursor = collection.find(search_query).sort("order", 1)
            
            documents = await cursor.to_list(length=None)
            return [self._document_to_activity(doc) for doc in documents]
        except Exception as e:
            raise DatabaseError(f"Error searching activities: {str(e)}")
    # endregion

    # region Count Methods
    async def count_by_day_id(self, day_id: str) -> int:
        """Counts non-deleted activities for a given day."""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({
                "day_id": day_id, 
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            raise DatabaseError(f"Error counting activities by day ID: {str(e)}")

    async def count_by_status(self, day_id: str, status: str) -> int:
        """Counts activities for a given day and status."""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({
                "day_id": day_id, 
                "status": status, 
                "is_deleted": {"$ne": True}
            })
        except Exception as e:
            raise DatabaseError(f"Error counting activities by status: {str(e)}")

    async def count_by_trip_id(self, trip_id: str) -> int:
        """Counts all activities for a given trip."""
        try:
            collection = await self._get_collection()
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
                {"$count": "total"}
            ]
            result = await collection.aggregate(pipeline).to_list(length=1)
            return result[0]["total"] if result else 0
        except Exception as e:
            raise DatabaseError(f"Error counting activities by trip ID: {str(e)}")

    async def get_next_order(self, day_id: str) -> int:
        """Gets the next available order number for a new activity on a given day."""
        try:
            collection = await self._get_collection()
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
                        "max_order": {"$max": "$order"}
                    }
                }
            ]
            result = await collection.aggregate(pipeline).to_list(length=1)
            return (result[0]["max_order"] + 1) if result and result[0]["max_order"] is not None else 1
        except Exception as e:
            raise DatabaseError(f"Error getting next order: {str(e)}")
    # endregion

    # region Bulk & Batch Operations
    async def delete_by_day_id(self, day_id: str) -> bool:
        """Soft deletes all activities associated with a day ID."""
        try:
            collection = await self._get_collection()
            result = await collection.update_many(
                {"day_id": day_id},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting activities by day ID: {str(e)}")

    async def delete_by_trip_id(self, trip_id: str) -> bool:
        """Soft deletes all activities associated with a trip ID."""
        try:
            collection = await self._get_collection()
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
                        "day.trip_id": trip_id
                    }
                },
                {"$project": {"_id": 1}}
            ]
            activities = await collection.aggregate(pipeline).to_list(length=None)
            activity_ids = [act["_id"] for act in activities]
            
            if not activity_ids:
                return False
            
            result = await collection.update_many(
                {"_id": {"$in": activity_ids}},
                {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error deleting activities by trip ID: {str(e)}")

    async def bulk_update_order(self, activity_orders: List[Dict[str, Any]]) -> bool:
        """Updates the order of multiple activities in a single bulk operation."""
        try:
            collection = await self._get_collection()
            if not activity_orders:
                return False
            
            # ✅ CORREGIDO: Usar string IDs directamente
            operations = [
                {
                    "updateOne": {
                        "filter": {"_id": item["activity_id"]},
                        "update": {"$set": {"order": item["order"], "updated_at": datetime.utcnow()}}
                    }
                } for item in activity_orders
            ]
            result = await collection.bulk_write(operations)
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f"Error in bulk update of activity order: {str(e)}")
    # endregion

    # region Statistics & Utility Methods
    async def get_day_activity_statistics(self, day_id: str) -> Dict[str, Any]:
        """Gets comprehensive statistics for activities in a day."""
        try:
            collection = await self._get_collection()
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
                            "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                        },
                        "pending_activities": {
                            "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                        },
                        "cancelled_activities": {
                            "$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}
                        },
                        "total_estimated_cost": {"$sum": "$estimated_cost"},
                        "total_actual_cost": {"$sum": "$actual_cost"},
                        "categories": {"$addToSet": "$category"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                stats.pop("_id", None)
                return stats
            else:
                return {
                    "total_activities": 0,
                    "completed_activities": 0,
                    "pending_activities": 0,
                    "cancelled_activities": 0,
                    "total_estimated_cost": 0.0,
                    "total_actual_cost": 0.0,
                    "categories": []
                }
                
        except Exception as e:
            raise DatabaseError(f"Error getting day activity statistics: {str(e)}")

    async def get_trip_activity_statistics(self, trip_id: str) -> Dict[str, Any]:
        """Gets comprehensive statistics for activities in a trip."""
        try:
            collection = await self._get_collection()
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
                            "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                        },
                        "pending_activities": {
                            "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                        },
                        "in_progress_activities": {
                            "$sum": {"$cond": [{"$eq": ["$status", "in_progress"]}, 1, 0]}
                        },
                        "cancelled_activities": {
                            "$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}
                        },
                        "total_estimated_cost": {"$sum": "$estimated_cost"},
                        "total_actual_cost": {"$sum": "$actual_cost"},
                        "categories": {"$addToSet": "$category"},
                        "avg_cost_per_activity": {"$avg": "$estimated_cost"}
                    }
                }
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                stats.pop("_id", None)
                
                # Calcular porcentaje de finalización
                total = stats.get("total_activities", 0)
                completed = stats.get("completed_activities", 0)
                stats["completion_percentage"] = (completed / total * 100) if total > 0 else 0.0
                
                return stats
            else:
                return {
                    "total_activities": 0,
                    "completed_activities": 0,
                    "pending_activities": 0,
                    "in_progress_activities": 0,
                    "cancelled_activities": 0,
                    "total_estimated_cost": 0.0,
                    "total_actual_cost": 0.0,
                    "categories": [],
                    "avg_cost_per_activity": 0.0,
                    "completion_percentage": 0.0
                }
                
        except Exception as e:
            raise DatabaseError(f"Error getting trip activity statistics: {str(e)}")
    # endregion

    # MÉTODOS AUXILIARES
    def _activity_to_document(self, activity_data: ActivityData) -> Dict[str, Any]:
        """Converts an Activity domain object to a MongoDB document."""
        # ✅ CORREGIDO: Manejar campos time correctamente para MongoDB
        start_time = activity_data.start_time
        if isinstance(start_time, time):
            # Convertir time a datetime para MongoDB (usando fecha base)
            start_time = datetime.combine(datetime.today().date(), start_time)
        elif start_time is None:
            start_time = None
            
        end_time = activity_data.end_time
        if isinstance(end_time, time):
            # Convertir time a datetime para MongoDB (usando fecha base)
            end_time = datetime.combine(datetime.today().date(), end_time)
        elif end_time is None:
            end_time = None

        return {
            "_id": activity_data.id,
            "day_id": activity_data.day_id,
            "title": activity_data.title,
            "description": activity_data.description,
            "location": activity_data.location,
            "start_time": start_time,
            "end_time": end_time,
            "estimated_cost": activity_data.estimated_cost or 0.0,
            "actual_cost": activity_data.actual_cost or 0.0,
            "category": activity_data.category,
            "status": activity_data.status.value if isinstance(activity_data.status, ActivityStatus) else activity_data.status,
            "order": activity_data.order or 1,
            "created_by": activity_data.created_by,
            "is_deleted": activity_data.is_deleted or False,
            "created_at": activity_data.created_at or datetime.utcnow(),
            "updated_at": activity_data.updated_at or datetime.utcnow()
        }

    def _document_to_activity(self, document: Dict[str, Any]) -> Activity:
        """Converts a MongoDB document to an Activity domain object."""
        # ✅ CORREGIDO: Convertir datetime de vuelta a time para el dominio
        start_time = document.get("start_time")
        if isinstance(start_time, datetime):
            start_time = start_time.time()
            
        end_time = document.get("end_time")
        if isinstance(end_time, datetime):
            end_time = end_time.time()

        activity_data = ActivityData(
            id=str(document["_id"]),
            day_id=document.get("day_id"),
            title=document.get("title"),
            description=document.get("description"),
            location=document.get("location"),
            start_time=start_time,
            end_time=end_time,
            estimated_cost=document.get("estimated_cost", 0.0),
            actual_cost=document.get("actual_cost", 0.0),
            category=document.get("category"),
            status=document.get("status", "pending"),
            order=document.get("order", 1),
            created_by=document.get("created_by"),
            is_deleted=document.get("is_deleted", False),
            created_at=document.get("created_at"),
            updated_at=document.get("updated_at")
        )
        
        return Activity.from_data(activity_data)