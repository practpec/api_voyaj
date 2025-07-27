# src/modules/trips/infrastructure/repositories/trip_member_mongo_repository.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId

from ...domain.trip_member import TripMember, TripMemberData, TripMemberRole, TripMemberStatus
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.database.Connection import DatabaseConnection
from shared.errors.custom_errors import DatabaseError


class TripMemberMongoRepository(ITripMemberRepository):
    def __init__(self):
        self._db_connection = DatabaseConnection()
        self._collection_name = "trip_members"

    async def _get_collection(self) -> AsyncIOMotorCollection:
        """Obtener colección de miembros de viaje"""
        database = self._db_connection.get_database()
        return database[self._collection_name]

    def _member_to_document(self, member_data: TripMemberData) -> Dict[str, Any]:
        """Convertir entidad TripMember a documento MongoDB"""
        doc = {
            "_id": member_data.id,
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
        """Convertir documento MongoDB a entidad TripMember"""
        if not document:
            return None
            
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

    async def create(self, trip_member: TripMember) -> TripMember:
        """Crear nuevo miembro de viaje"""
        try:
            collection = await self._get_collection()
            member_data = self._member_to_document(trip_member.to_public_data())
            
            result = await collection.insert_one(member_data)
            member_data["_id"] = result.inserted_id
            
            return self._document_to_member(member_data)
            
        except Exception as error:
            raise DatabaseError(f"Error creando miembro de viaje: {str(error)}")

    async def find_by_id(self, member_id: str) -> Optional[TripMember]:
        """Buscar miembro por ID"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "_id": member_id,
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_member(document) if document else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembro por ID: {str(error)}")

    async def update(self, trip_member: TripMember) -> TripMember:
        """Actualizar miembro de viaje"""
        try:
            collection = await self._get_collection()
            member_data = self._member_to_document(trip_member.to_public_data())
            member_data.pop("_id", None)
            
            await collection.update_one(
                {"_id": trip_member.id},
                {"$set": member_data}
            )
            
            return trip_member
            
        except Exception as error:
            raise DatabaseError(f"Error actualizando miembro: {str(error)}")

    async def delete(self, member_id: str) -> bool:
        """Eliminar miembro (soft delete)"""
        try:
            collection = await self._get_collection()
            result = await collection.update_one(
                {"_id": member_id},
                {"$set": {"is_deleted": True}}
            )
            
            return result.modified_count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error eliminando miembro: {str(error)}")

    async def find_by_trip_id(
        self, 
        trip_id: str, 
        page: int = 1, 
        limit: int = 50
    ) -> tuple[List[TripMember], int]:
        """Buscar miembros por ID de viaje"""
        try:
            collection = await self._get_collection()
            query = {
                "trip_id": trip_id,
                "is_deleted": {"$ne": True}
            }
            
            skip = (page - 1) * limit
            
            cursor = collection.find(query).sort("invited_at", 1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            total = await collection.count_documents(query)
            
            members = [self._document_to_member(doc) for doc in documents]
            return members, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembros por viaje: {str(error)}")

    async def find_active_members_by_trip_id(self, trip_id: str) -> List[TripMember]:
        """Buscar miembros activos por ID de viaje"""
        try:
            collection = await self._get_collection()
            query = {
                "trip_id": trip_id,
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("joined_at", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembros activos: {str(error)}")

    async def find_pending_members_by_trip_id(self, trip_id: str) -> List[TripMember]:
        """Buscar miembros pendientes por ID de viaje"""
        try:
            collection = await self._get_collection()
            query = {
                "trip_id": trip_id,
                "status": TripMemberStatus.PENDING.value,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("invited_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembros pendientes: {str(error)}")

    async def find_trip_owner(self, trip_id: str) -> Optional[TripMember]:
        """Buscar propietario del viaje"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "trip_id": trip_id,
                "role": TripMemberRole.OWNER.value,
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_member(document) if document else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando propietario: {str(error)}")

    async def find_trip_admins(self, trip_id: str) -> List[TripMember]:
        """Buscar administradores del viaje"""
        try:
            collection = await self._get_collection()
            query = {
                "trip_id": trip_id,
                "role": {"$in": [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]},
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("joined_at", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando administradores: {str(error)}")

    async def find_by_user_id(
        self, 
        user_id: str, 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[TripMember], int]:
        """Buscar miembros por ID de usuario"""
        try:
            collection = await self._get_collection()
            query = {
                "user_id": user_id,
                "is_deleted": {"$ne": True}
            }
            
            skip = (page - 1) * limit
            
            cursor = collection.find(query).sort("invited_at", -1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            total = await collection.count_documents(query)
            
            members = [self._document_to_member(doc) for doc in documents]
            return members, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembros por usuario: {str(error)}")

    async def find_active_by_user_id(self, user_id: str) -> List[TripMember]:
        """Buscar membresías activas por ID de usuario"""
        try:
            collection = await self._get_collection()
            query = {
                "user_id": user_id,
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("joined_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando membresías activas: {str(error)}")

    async def find_pending_invitations_by_user_id(self, user_id: str) -> List[TripMember]:
        """Buscar invitaciones pendientes por ID de usuario"""
        try:
            collection = await self._get_collection()
            query = {
                "user_id": user_id,
                "status": TripMemberStatus.PENDING.value,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("invited_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando invitaciones pendientes: {str(error)}")

    async def find_user_trips_with_role(self, user_id: str, role: str) -> List[TripMember]:
        """Buscar viajes de usuario con rol específico"""
        try:
            collection = await self._get_collection()
            query = {
                "user_id": user_id,
                "role": role,
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("joined_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando viajes con rol: {str(error)}")

    async def find_by_trip_and_user(
        self, 
        trip_id: str, 
        user_id: str
    ) -> Optional[TripMember]:
        """Buscar miembro específico por viaje y usuario"""
        try:
            collection = await self._get_collection()
            document = await collection.find_one({
                "trip_id": trip_id,
                "user_id": user_id,
                "is_deleted": {"$ne": True}
            })
            
            return self._document_to_member(document) if document else None
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembro específico: {str(error)}")

    async def find_by_trip_and_role(self, trip_id: str, role: str) -> List[TripMember]:
        """Buscar miembros por viaje y rol"""
        try:
            collection = await self._get_collection()
            query = {
                "trip_id": trip_id,
                "role": role,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("joined_at", 1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembros por rol: {str(error)}")

    async def find_by_trip_and_status(self, trip_id: str, status: str) -> List[TripMember]:
        """Buscar miembros por viaje y estado"""
        try:
            collection = await self._get_collection()
            query = {
                "trip_id": trip_id,
                "status": status,
                "is_deleted": {"$ne": True}
            }
            
            cursor = collection.find(query).sort("invited_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error buscando miembros por estado: {str(error)}")

    async def exists_by_trip_and_user(self, trip_id: str, user_id: str) -> bool:
        """Verificar si existe membresía específica"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "trip_id": trip_id,
                "user_id": user_id,
                "is_deleted": {"$ne": True}
            })
            
            return count > 0
            
        except Exception:
            return False

    async def is_user_member_of_trip(self, trip_id: str, user_id: str) -> bool:
        """Verificar si usuario es miembro activo del viaje"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "trip_id": trip_id,
                "user_id": user_id,
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            })
            
            return count > 0
            
        except Exception:
            return False

    async def is_user_owner_of_trip(self, trip_id: str, user_id: str) -> bool:
        """Verificar si usuario es propietario del viaje"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "trip_id": trip_id,
                "user_id": user_id,
                "role": TripMemberRole.OWNER.value,
                "is_deleted": {"$ne": True}
            })
            
            return count > 0
            
        except Exception:
            return False

    async def is_user_admin_of_trip(self, trip_id: str, user_id: str) -> bool:
        """Verificar si usuario es administrador del viaje"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "trip_id": trip_id,
                "user_id": user_id,
                "role": {"$in": [TripMemberRole.OWNER.value, TripMemberRole.ADMIN.value]},
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            })
            
            return count > 0
            
        except Exception:
            return False

    async def can_user_access_trip(self, trip_id: str, user_id: str) -> bool:
        """Verificar si usuario puede acceder al viaje"""
        try:
            collection = await self._get_collection()
            count = await collection.count_documents({
                "trip_id": trip_id,
                "user_id": user_id,
                "status": {"$in": [TripMemberStatus.ACCEPTED.value, TripMemberStatus.PENDING.value]},
                "is_deleted": {"$ne": True}
            })
            
            return count > 0
            
        except Exception:
            return False

    async def count_members_by_trip_id(self, trip_id: str) -> int:
        """Contar miembros por ID de viaje"""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({
                "trip_id": trip_id,
                "is_deleted": {"$ne": True}
            })
            
        except Exception:
            return 0

    async def count_active_members_by_trip_id(self, trip_id: str) -> int:
        """Contar miembros activos por ID de viaje"""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({
                "trip_id": trip_id,
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception:
            return 0

    async def count_pending_members_by_trip_id(self, trip_id: str) -> int:
        """Contar miembros pendientes por ID de viaje"""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({
                "trip_id": trip_id,
                "status": TripMemberStatus.PENDING.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception:
            return 0

    async def count_trips_by_user_id(self, user_id: str) -> int:
        """Contar viajes por ID de usuario"""
        try:
            collection = await self._get_collection()
            return await collection.count_documents({
                "user_id": user_id,
                "status": TripMemberStatus.ACCEPTED.value,
                "is_deleted": {"$ne": True}
            })
            
        except Exception:
            return 0

    async def delete_by_trip_id(self, trip_id: str) -> bool:
        """Eliminar todos los miembros de un viaje"""
        try:
            collection = await self._get_collection()
            result = await collection.update_many(
                {"trip_id": trip_id},
                {"$set": {"is_deleted": True}}
            )
            
            return result.modified_count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error eliminando miembros por viaje: {str(error)}")

    async def delete_by_user_id(self, user_id: str) -> bool:
        """Eliminar todas las membresías de un usuario"""
        try:
            collection = await self._get_collection()
            result = await collection.update_many(
                {"user_id": user_id},
                {"$set": {"is_deleted": True}}
            )
            
            return result.modified_count > 0
            
        except Exception as error:
            raise DatabaseError(f"Error eliminando membresías por usuario: {str(error)}")

    async def cleanup_rejected_invitations(self, older_than_days: int) -> int:
        """Limpiar invitaciones rechazadas antiguas"""
        try:
            collection = await self._get_collection()
            cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
            
            result = await collection.delete_many({
                "status": TripMemberStatus.REJECTED.value,
                "invited_at": {"$lt": cutoff_date}
            })
            
            return result.deleted_count
            
        except Exception as error:
            raise DatabaseError(f"Error limpiando invitaciones: {str(error)}")

    async def search(self, query: str, trip_id: Optional[str] = None) -> List[TripMember]:
        """Buscar miembros por texto"""
        try:
            collection = await self._get_collection()
            search_query = {
                "notes": {"$regex": query, "$options": "i"},
                "is_deleted": {"$ne": True}
            }
            
            if trip_id:
                search_query["trip_id"] = trip_id
            
            cursor = collection.find(search_query).sort("invited_at", -1)
            documents = await cursor.to_list(length=None)
            
            return [self._document_to_member(doc) for doc in documents]
            
        except Exception as error:
            raise DatabaseError(f"Error en búsqueda de miembros: {str(error)}")

    async def find_with_filters(
        self, 
        filters: Dict[str, Any], 
        page: int = 1, 
        limit: int = 20
    ) -> tuple[List[TripMember], int]:
        """Buscar miembros con filtros"""
        try:
            collection = await self._get_collection()
            query = {"is_deleted": {"$ne": True}}
            
            for key, value in filters.items():
                if value is not None:
                    query[key] = value
            
            skip = (page - 1) * limit
            
            cursor = collection.find(query).sort("invited_at", -1).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            total = await collection.count_documents(query)
            
            members = [self._document_to_member(doc) for doc in documents]
            return members, total
            
        except Exception as error:
            raise DatabaseError(f"Error buscando con filtros: {str(error)}")

    async def count_by_filters(self, filters: Dict[str, Any]) -> int:
        """Contar miembros con filtros"""
        try:
            collection = await self._get_collection()
            query = {"is_deleted": {"$ne": True}}
            
            for key, value in filters.items():
                if value is not None:
                    query[key] = value
            
            return await collection.count_documents(query)
            
        except Exception:
            return 0