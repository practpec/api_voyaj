from typing import List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING

from ...domain.friendship import Friendship, FriendshipData
from ...domain.interfaces.friendship_repository import IFriendshipRepository
from shared.database.Connection import DatabaseConnection
from shared.constants import FRIENDSHIP_STATUS
from shared.errors.custom_errors import DatabaseError


class FriendshipMongoRepository(IFriendshipRepository):
    def __init__(self):
        self._db = DatabaseConnection.get_database()
        self._collection: AsyncIOMotorCollection = self._db.friendships
        self._create_indexes()

    def _create_indexes(self) -> None:
        """Crear índices para optimizar consultas"""
        # Índice compuesto para buscar relaciones entre usuarios
        self._collection.create_index([
            ("user_id", ASCENDING),
            ("friend_id", ASCENDING),
            ("status", ASCENDING),
            ("is_deleted", ASCENDING)
        ])
        
        # Índice para buscar solicitudes recibidas
        self._collection.create_index([
            ("friend_id", ASCENDING),
            ("status", ASCENDING),
            ("is_deleted", ASCENDING)
        ])
        
        # Índice para buscar solicitudes enviadas
        self._collection.create_index([
            ("user_id", ASCENDING),
            ("status", ASCENDING),
            ("is_deleted", ASCENDING)
        ])

    async def create(self, friendship: Friendship) -> Friendship:
        """Crear nueva amistad"""
        try:
            friendship_data = friendship.to_data()
            doc = {
                "id": friendship_data.id,
                "user_id": friendship_data.user_id,
                "friend_id": friendship_data.friend_id,
                "status": friendship_data.status,
                "created_at": friendship_data.created_at,
                "accepted_at": friendship_data.accepted_at,
                "is_deleted": friendship_data.is_deleted
            }
            
            await self._collection.insert_one(doc)
            return friendship
            
        except Exception as error:
            raise DatabaseError(f"Error creando amistad: {str(error)}")

    async def find_by_id(self, friendship_id: str) -> Optional[Friendship]:
        """Buscar amistad por ID"""
        try:
            doc = await self._collection.find_one({
                "id": friendship_id,
                "is_deleted": False
            })
            
            return Friendship.from_data(FriendshipData(**doc)) if doc else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando amistad: {str(error)}")

    async def update(self, friendship: Friendship) -> Friendship:
        """Actualizar amistad"""
        try:
            friendship_data = friendship.to_data()
            update_doc = {
                "status": friendship_data.status,
                "accepted_at": friendship_data.accepted_at,
                "is_deleted": friendship_data.is_deleted
            }
            
            await self._collection.update_one(
                {"id": friendship_data.id},
                {"$set": update_doc}
            )
            
            return friendship
            
        except Exception as error:
            raise DatabaseError(f"Error actualizando amistad: {str(error)}")

    async def delete(self, friendship_id: str) -> bool:
        """Eliminar amistad (soft delete)"""
        try:
            result = await self._collection.update_one(
                {"id": friendship_id},
                {"$set": {"is_deleted": True}}
            )
            
            return result.modified_count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error eliminando amistad: {str(error)}")

    async def find_between_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Buscar amistad entre dos usuarios específicos"""
        try:
            doc = await self._collection.find_one({
                "$or": [
                    {"user_id": user_id, "friend_id": friend_id},
                    {"user_id": friend_id, "friend_id": user_id}
                ],
                "is_deleted": False
            })
            
            return Friendship.from_data(FriendshipData(**doc)) if doc else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando amistad entre usuarios: {str(error)}")

    async def find_accepted_between_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Buscar amistad aceptada entre dos usuarios"""
        try:
            doc = await self._collection.find_one({
                "$or": [
                    {"user_id": user_id, "friend_id": friend_id},
                    {"user_id": friend_id, "friend_id": user_id}
                ],
                "status": FRIENDSHIP_STATUS["ACCEPTED"],
                "is_deleted": False
            })
            
            return Friendship.from_data(FriendshipData(**doc)) if doc else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando amistad aceptada: {str(error)}")

    async def find_pending_between_users(self, user_id: str, friend_id: str) -> Optional[Friendship]:
        """Buscar solicitud pendiente entre dos usuarios"""
        try:
            doc = await self._collection.find_one({
                "$or": [
                    {"user_id": user_id, "friend_id": friend_id},
                    {"user_id": friend_id, "friend_id": user_id}
                ],
                "status": FRIENDSHIP_STATUS["PENDING"],
                "is_deleted": False
            })
            
            return Friendship.from_data(FriendshipData(**doc)) if doc else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando solicitud pendiente: {str(error)}")

    async def find_user_friends(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Friendship], int]:
        """Buscar amigos aceptados de un usuario con paginación"""
        try:
            skip = (page - 1) * limit
            
            query = {
                "$or": [
                    {"user_id": user_id},
                    {"friend_id": user_id}
                ],
                "status": FRIENDSHIP_STATUS["ACCEPTED"],
                "is_deleted": False
            }
            
            # Obtener total de documentos
            total = await self._collection.count_documents(query)
            
            # Obtener documentos paginados
            cursor = self._collection.find(query).skip(skip).limit(limit).sort("accepted_at", DESCENDING)
            docs = await cursor.to_list(length=limit)
            
            friendships = [Friendship.from_data(FriendshipData(**doc)) for doc in docs]
            
            return friendships, total
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo amigos: {str(error)}")

    async def find_pending_requests_received(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Friendship], int]:
        """Buscar solicitudes pendientes recibidas por un usuario"""
        try:
            skip = (page - 1) * limit
            
            query = {
                "friend_id": user_id,
                "status": FRIENDSHIP_STATUS["PENDING"],
                "is_deleted": False
            }
            
            total = await self._collection.count_documents(query)
            
            cursor = self._collection.find(query).skip(skip).limit(limit).sort("created_at", DESCENDING)
            docs = await cursor.to_list(length=limit)
            
            friendships = [Friendship.from_data(FriendshipData(**doc)) for doc in docs]
            
            return friendships, total
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo solicitudes recibidas: {str(error)}")

    async def find_pending_requests_sent(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[Friendship], int]:
        """Buscar solicitudes pendientes enviadas por un usuario"""
        try:
            skip = (page - 1) * limit
            
            query = {
                "user_id": user_id,
                "status": FRIENDSHIP_STATUS["PENDING"],
                "is_deleted": False
            }
            
            total = await self._collection.count_documents(query)
            
            cursor = self._collection.find(query).skip(skip).limit(limit).sort("created_at", DESCENDING)
            docs = await cursor.to_list(length=limit)
            
            friendships = [Friendship.from_data(FriendshipData(**doc)) for doc in docs]
            
            return friendships, total
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo solicitudes enviadas: {str(error)}")

    async def count_user_friends(self, user_id: str) -> int:
        """Contar amigos de un usuario"""
        try:
            return await self._collection.count_documents({
                "$or": [
                    {"user_id": user_id},
                    {"friend_id": user_id}
                ],
                "status": FRIENDSHIP_STATUS["ACCEPTED"],
                "is_deleted": False
            })
            
        except Exception as error:
            raise DatabaseError(f"Error contando amigos: {str(error)}")

    async def count_pending_requests_received(self, user_id: str) -> int:
        """Contar solicitudes pendientes recibidas"""
        try:
            return await self._collection.count_documents({
                "friend_id": user_id,
                "status": FRIENDSHIP_STATUS["PENDING"],
                "is_deleted": False
            })
            
        except Exception as error:
            raise DatabaseError(f"Error contando solicitudes recibidas: {str(error)}")

    async def count_pending_requests_sent(self, user_id: str) -> int:
        """Contar solicitudes pendientes enviadas"""
        try:
            return await self._collection.count_documents({
                "user_id": user_id,
                "status": FRIENDSHIP_STATUS["PENDING"],
                "is_deleted": False
            })
            
        except Exception as error:
            raise DatabaseError(f"Error contando solicitudes enviadas: {str(error)}")

    async def find_accepted_friends_ids(self, user_id: str) -> List[str]:
        """Obtener IDs de amigos aceptados de un usuario"""
        try:
            cursor = self._collection.find({
                "$or": [
                    {"user_id": user_id},
                    {"friend_id": user_id}
                ],
                "status": FRIENDSHIP_STATUS["ACCEPTED"],
                "is_deleted": False
            }, {"user_id": 1, "friend_id": 1})
            
            docs = await cursor.to_list(length=None)
            
            friend_ids = []
            for doc in docs:
                if doc["user_id"] == user_id:
                    friend_ids.append(doc["friend_id"])
                else:
                    friend_ids.append(doc["user_id"])
            
            return friend_ids
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo IDs de amigos: {str(error)}")