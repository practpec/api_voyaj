# src/modules/friendships/infrastructure/repositories/friendship_mongo_repository.py
from typing import List, Optional, Tuple
from pymongo import DESCENDING

from ...domain.Friendship import Friendship, FriendshipData
from ...domain.interfaces.IFriendshipRepository import IFriendshipRepository
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError
from shared.constants import FRIENDSHIP_STATUS


class FriendshipMongoRepository(IFriendshipRepository):
    def __init__(self):
        self._db = DatabaseConnection.get_database()
        self._collection = self._db.friendships

    def _document_to_friendship_data(self, doc) -> FriendshipData:
        """Convertir documento MongoDB a FriendshipData"""
        # Convertir _id a id si existe
        if "_id" in doc:
            doc["id"] = doc.pop("_id")
        
        return FriendshipData(**doc)

    async def create(self, friendship: Friendship) -> Friendship:
        """Crear nueva amistad"""
        try:
            friendship_data = friendship.to_data()
            doc = {
                "_id": friendship_data.id,  # MongoDB usa _id
                "id": friendship_data.id,   # También mantener id para compatibilidad
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
                "$or": [
                    {"_id": friendship_id},
                    {"id": friendship_id}
                ],
                "is_deleted": False
            })
            
            return Friendship.from_data(self._document_to_friendship_data(doc)) if doc else None
            
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
                {"$or": [{"_id": friendship_data.id}, {"id": friendship_data.id}]},
                {"$set": update_doc}
            )
            
            return friendship
            
        except Exception as error:
            raise DatabaseError(f"Error actualizando amistad: {str(error)}")

    async def delete(self, friendship_id: str) -> bool:
        """Eliminar amistad (soft delete)"""
        try:
            result = await self._collection.update_one(
                {"$or": [{"_id": friendship_id}, {"id": friendship_id}]},
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
            
            return Friendship.from_data(self._document_to_friendship_data(doc)) if doc else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando amistad entre usuarios: {str(error)}")

    async def find_user_friends(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Friendship], int]:
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
            
            friendships = [Friendship.from_data(self._document_to_friendship_data(doc)) for doc in docs]
            
            return friendships, total
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo amigos del usuario: {str(error)}")

    async def find_pending_requests_received(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Friendship], int]:
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
            
            friendships = [Friendship.from_data(self._document_to_friendship_data(doc)) for doc in docs]
            
            return friendships, total
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo solicitudes recibidas: {str(error)}")

    async def find_pending_requests_sent(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> Tuple[List[Friendship], int]:
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
            
            friendships = [Friendship.from_data(self._document_to_friendship_data(doc)) for doc in docs]
            
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

    async def get_all_users_except(self, user_id: str, limit: int = 10) -> List[str]:
        """Obtener usuarios que no son amigos para sugerencias"""
        try:
            # Obtener amigos actuales
            current_friends = await self.find_accepted_friends_ids(user_id)
            
            # Obtener usuarios que tienen solicitudes pendientes
            pending_users = set()
            
            # Solicitudes enviadas
            sent_cursor = self._collection.find({
                "user_id": user_id,
                "status": FRIENDSHIP_STATUS["PENDING"],
                "is_deleted": False
            }, {"friend_id": 1})
            sent_docs = await sent_cursor.to_list(length=None)
            for doc in sent_docs:
                pending_users.add(doc["friend_id"])
            
            # Solicitudes recibidas
            received_cursor = self._collection.find({
                "friend_id": user_id,
                "status": FRIENDSHIP_STATUS["PENDING"],
                "is_deleted": False
            }, {"user_id": 1})
            received_docs = await received_cursor.to_list(length=None)
            for doc in received_docs:
                pending_users.add(doc["user_id"])
            
            # Usuarios a excluir
            excluded_users = set(current_friends) | pending_users | {user_id}
            
            # Buscar usuarios en la colección de usuarios
            # La colección users usa _id como campo principal
            users_collection = self._db.users
            cursor = users_collection.find({
                "_id": {"$nin": list(excluded_users)},
                "esta_activo": True,
                "email_verificado": True,
                "eliminado": False
            }, {"_id": 1}).limit(limit)
            
            user_docs = await cursor.to_list(length=limit)
            return [doc["_id"] for doc in user_docs]
            
        except Exception as error:
            raise DatabaseError(f"Error obteniendo usuarios sugeridos: {str(error)}")