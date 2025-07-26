from motor.motor_asyncio import AsyncIOMotorCollection
from typing import Optional, List, Dict, Any
from ...domain.User import User
from ...domain.interfaces.IUserRepository import IUserRepository
from shared.database.Connection import DatabaseConnection

class UserMongoRepository(IUserRepository):
    def __init__(self):
        self.db = DatabaseConnection.get_database()
        self.collection: AsyncIOMotorCollection = self.db["users"]
        
    async def create(self, user: User) -> None:
        user_data = user.to_dict()
        user_data["contrasena_hash"] = user._contrasena_hash
        del user_data["id"]
        user_data["_id"] = user.id
        await self.collection.insert_one(user_data)
    
    async def find_by_id(self, user_id: str) -> Optional[User]:
        user_data = await self.collection.find_one({"_id": user_id, "eliminado": False})
        if not user_data:
            return None
        return self._document_to_user(user_data)
    
    async def find_by_email(self, email: str) -> Optional[User]:
        user_data = await self.collection.find_one({
            "correo_electronico": email.lower(),
            "eliminado": False
        })
        if not user_data:
            return None
        return self._document_to_user(user_data)
    
    async def update(self, user: User) -> None:
        user_data = user.to_dict()
        user_data["contrasena_hash"] = user._contrasena_hash
        del user_data["id"]
        
        await self.collection.update_one(
            {"_id": user.id},
            {"$set": user_data}
        )
    
    async def delete(self, user_id: str) -> None:
        await self.collection.update_one(
            {"_id": user_id},
            {"$set": {"eliminado": True, "esta_activo": False}}
        )
    
    async def search_users(self, query: str, limit: int = 10, offset: int = 0) -> List[User]:
        cursor = self.collection.find({
            "$and": [
                {"eliminado": False},
                {"esta_activo": True},
                {
                    "$or": [
                        {"nombre": {"$regex": query, "$options": "i"}},
                        {"correo_electronico": {"$regex": query, "$options": "i"}}
                    ]
                }
            ]
        }).skip(offset).limit(limit)
        
        users = []
        async for user_data in cursor:
            users.append(self._document_to_user(user_data))
        
        return users
    
    async def count_users(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = {"eliminado": False}
        if filters:
            query.update(filters)
        return await self.collection.count_documents(query)
    
    async def exists_by_email(self, email: str) -> bool:
        count = await self.collection.count_documents({
            "correo_electronico": email.lower(),
            "eliminado": False
        })
        return count > 0
    
    def _document_to_user(self, doc: Dict[str, Any]) -> User:
        doc["id"] = doc["_id"]
        doc["contrasena_hash"] = doc.get("contrasena_hash", "")
        return User.from_dict(doc)
    
