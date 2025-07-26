from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from ...domain.trip_member import TripMember, TripMemberData, TripMemberRole, TripMemberStatus
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.database.Connection import DatabaseConnection


class TripMemberMongoRepository(ITripMemberRepository):
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self._db = db or DatabaseConnection()
        self._collection = self._db.trip_members

    async def create(self, trip_member: TripMember) -> TripMember:
        member_data = self._member_to_document(trip_member.to_public_data())
        
        result = await self._collection.insert_one(member_data)
        member_data["_id"] = result.inserted_id
        
        return self._document_to_member(member_data)

    async def find_by_id(self, member_id: str) -> Optional[TripMember]:
        try:
            document = await self._collection.find_one({
                "_id": ObjectId(member_id),
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_member(document) if document else None
        except Exception:
            return None

    async def update(self, trip_member: TripMember) -> TripMember:
        member_data = self._member_to_document(trip_member.to_public_data())
        member_data.pop("_id", None)
        
        await self._collection.update_one(
            {"_id": ObjectId(trip_member.id)},
            {"$set": member_data}
        )
        
        return trip_member

    async def delete(self, member_id: str) -> bool:
        result = await self._collection.update_one(
            {"_id": ObjectId(member_id)},
            {"$set": {"is_deleted": True}}
        )
        
        return result.modified_count > 0

    async def find_by_trip_id(
        self, 
        trip_id: str, 
        page: int = 1, 
        limit: int = 50
    ) -> tuple[List[TripMember], int]:
        query = {
            "trip_id": trip_id,
            "is_deleted": {"$ne": True}
        }
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("invited_at", 1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        members = [self._document_to_member(doc) for doc in documents]
        return members, total

    async def find_active_members_by_trip_id(self, trip_id: str) -> List[TripMember]:
        query = {
            "trip_id": trip_id,
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("joined_at", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_pending_members_by_trip_id(self, trip_id: str) -> List[TripMember]:
        query = {
            "trip_id": trip_id,
            "status": TripMemberStatus.PENDING.value,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("invited_at", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_trip_owner(self, trip_id: str) -> Optional[TripMember]:
        document = await self._collection.find_one({
            "trip_id": trip_id,
            "role": TripMemberRole.OWNER.value,
            "is_deleted": {"$ne": True}
        })
        
        return self._document_to_member(document) if document else None

    async def find_trip_admins(self, trip_id: str) -> List[TripMember]:
        query = {
            "trip_id": trip_id,
            "role": {"$in": [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]},
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("joined_at", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_by_user_id(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[TripMember], int]:
        query = {
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        }
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("invited_at", -1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        members = [self._document_to_member(doc) for doc in documents]
        return members, total

    async def find_active_by_user_id(self, user_id: str) -> List[TripMember]:
        query = {
            "user_id": user_id,
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("joined_at", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_pending_invitations_by_user_id(self, user_id: str) -> List[TripMember]:
        query = {
            "user_id": user_id,
            "status": TripMemberStatus.PENDING.value,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("invited_at", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_user_trips_with_role(self, user_id: str, role: str) -> List[TripMember]:
        query = {
            "user_id": user_id,
            "role": role,
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("joined_at", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_by_trip_and_user(
        self, 
        trip_id: str, 
        user_id: str
    ) -> Optional[TripMember]:
        document = await self._collection.find_one({
            "trip_id": trip_id,
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        })
        
        return self._document_to_member(document) if document else None

    async def find_by_trip_and_role(self, trip_id: str, role: str) -> List[TripMember]:
        query = {
            "trip_id": trip_id,
            "role": role,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("joined_at", 1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_by_trip_and_status(self, trip_id: str, status: str) -> List[TripMember]:
        query = {
            "trip_id": trip_id,
            "status": status,
            "is_deleted": {"$ne": True}
        }
        
        cursor = self._collection.find(query).sort("invited_at", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def exists_by_trip_and_user(self, trip_id: str, user_id: str) -> bool:
        count = await self._collection.count_documents({
            "trip_id": trip_id,
            "user_id": user_id,
            "is_deleted": {"$ne": True}
        })
        
        return count > 0

    async def is_user_member_of_trip(self, trip_id: str, user_id: str) -> bool:
        count = await self._collection.count_documents({
            "trip_id": trip_id,
            "user_id": user_id,
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        })
        
        return count > 0

    async def is_user_owner_of_trip(self, trip_id: str, user_id: str) -> bool:
        count = await self._collection.count_documents({
            "trip_id": trip_id,
            "user_id": user_id,
            "role": TripMemberRole.OWNER.value,
            "is_deleted": {"$ne": True}
        })
        
        return count > 0

    async def is_user_admin_of_trip(self, trip_id: str, user_id: str) -> bool:
        count = await self._collection.count_documents({
            "trip_id": trip_id,
            "user_id": user_id,
            "role": {"$in": [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]},
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        })
        
        return count > 0

    async def can_user_access_trip(self, trip_id: str, user_id: str) -> bool:
        count = await self._collection.count_documents({
            "trip_id": trip_id,
            "user_id": user_id,
            "status": {"$in": [TripMemberStatus.ACCEPTED.value, TripMemberStatus.PENDING.value]},
            "is_deleted": {"$ne": True}
        })
        
        return count > 0

    async def count_members_by_trip_id(self, trip_id: str) -> int:
        return await self._collection.count_documents({
            "trip_id": trip_id,
            "is_deleted": {"$ne": True}
        })

    async def count_active_members_by_trip_id(self, trip_id: str) -> int:
        return await self._collection.count_documents({
            "trip_id": trip_id,
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        })

    async def count_pending_members_by_trip_id(self, trip_id: str) -> int:
        return await self._collection.count_documents({
            "trip_id": trip_id,
            "status": TripMemberStatus.PENDING.value,
            "is_deleted": {"$ne": True}
        })

    async def count_trips_by_user_id(self, user_id: str) -> int:
        return await self._collection.count_documents({
            "user_id": user_id,
            "status": TripMemberStatus.ACCEPTED.value,
            "is_deleted": {"$ne": True}
        })

    async def search(self, query: str, trip_id: Optional[str] = None) -> List[TripMember]:
        search_query = {
            "notes": {"$regex": query, "$options": "i"},
            "is_deleted": {"$ne": True}
        }
        
        if trip_id:
            search_query["trip_id"] = trip_id
        
        cursor = self._collection.find(search_query).sort("invited_at", -1)
        documents = await cursor.to_list(length=None)
        
        return [self._document_to_member(doc) for doc in documents]

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[TripMember], int]:
        query = {"is_deleted": {"$ne": True}}
        
        for key, value in filters.items():
            if value is not None:
                query[key] = value
        
        skip = (page - 1) * limit
        
        cursor = self._collection.find(query).sort("invited_at", -1).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        total = await self._collection.count_documents(query)
        
        members = [self._document_to_member(doc) for doc in documents]
        return members, total

    async def count_by_filters(self, filters: Dict[str, Any]) -> int:
        query = {"is_deleted": {"$ne": True}}
        
        for key, value in filters.items():
            if value is not None:
                query[key] = value
        
        return await self._collection.count_documents(query)

    async def delete_by_trip_id(self, trip_id: str) -> bool:
        result = await self._collection.update_many(
            {"trip_id": trip_id},
            {"$set": {"is_deleted": True}}
        )
        
        return result.modified_count > 0

    async def delete_by_user_id(self, user_id: str) -> bool:
        result = await self._collection.update_many(
            {"user_id": user_id},
            {"$set": {"is_deleted": True}}
        )
        
        return result.modified_count > 0

    async def cleanup_rejected_invitations(self, older_than_days: int) -> int:
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        result = await self._collection.delete_many({
            "status": TripMemberStatus.REJECTED.value,
            "invited_at": {"$lt": cutoff_date}
        })
        
        return result.deleted_count

    def _member_to_document(self, member_data: TripMemberData) -> Dict[str, Any]:
        doc = {
            "_id": ObjectId(member_data.id),
            "trip_id": member_data.trip_id,
            "user_id": member_data.user_id,
            "role": member_data.role,
            "status": member_data.status,
            "notes": member_data.notes,
            "invited_by": member_data.invited_by,
            "invited_at": member_data.invited_at,
            "joined_at": member_data.joined_at,
            "left_at": member_data.left_at,
            "is_deleted": member_data.is_deleted
        }
        
        return {k: v for k, v in doc.items() if v is not None}

    def _document_to_member(self, document: Dict[str, Any]) -> TripMember:
        member_data = TripMemberData(
            id=str(document["_id"]),
            trip_id=document["trip_id"],
            user_id=document["user_id"],
            role=document["role"],
            status=document["status"],
            notes=document.get("notes"),
            invited_by=document.get("invited_by"),
            invited_at=document["invited_at"],
            joined_at=document.get("joined_at"),
            left_at=document.get("left_at"),
            is_deleted=document.get("is_deleted", False)
        )
        
        return TripMember.from_data(member_data)