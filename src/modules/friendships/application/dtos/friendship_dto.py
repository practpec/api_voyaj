# src/modules/friendships/application/dtos/friendship_dto.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Any, Dict
from ...domain.Friendship import FriendshipData


@dataclass
class SendFriendRequestDTO:
    friend_id: str


@dataclass
class FriendshipResponseDTO:
    id: str
    requester: Optional[Dict[str, Any]] = None
    recipient: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None


@dataclass
class UserInfoDTO:
    id: str
    name: str
    email: str
    profile_photo_url: Optional[str] = None


@dataclass
class FriendListResponseDTO:
    id: str
    friend_info: UserInfoDTO
    friendship_date: datetime
    mutual_friends_count: Optional[int] = None


@dataclass
class FriendRequestResponseDTO:
    id: str
    requester_info: UserInfoDTO
    request_date: datetime
    mutual_friends_count: Optional[int] = None


@dataclass
class FriendSuggestionDTO:
    id: str
    name: str
    email: str
    profile_photo_url: Optional[str]
    mutual_friends_count: int
    connection_reason: str = "Usuario recomendado"


@dataclass
class FriendshipStatsDTO:
    total_friends: int
    pending_requests_received: int
    pending_requests_sent: int


class FriendshipDTOMapper:
    
    @staticmethod
    def to_friendship_response(
        friendship: FriendshipData,
        requester_info: Optional[Dict[str, Any]] = None,
        recipient_info: Optional[Dict[str, Any]] = None
    ) -> FriendshipResponseDTO:
        return FriendshipResponseDTO(
            id=friendship.id,
            requester=requester_info,
            recipient=recipient_info,
            status=friendship.status,
            created_at=friendship.created_at,
            accepted_at=friendship.accepted_at
        )

    @staticmethod
    def to_friend_list_response(
        friendship: FriendshipData,
        friend_info: Dict[str, Any],
        mutual_friends_count: int = 0
    ) -> FriendListResponseDTO:
        return FriendListResponseDTO(
            id=friendship.id,
            friend_info=UserInfoDTO(
                id=friend_info.get("id"),
                name=friend_info.get("name") or friend_info.get("nombre"),
                email=friend_info.get("email") or friend_info.get("correo_electronico"),
                profile_photo_url=friend_info.get("profile_photo_url") or friend_info.get("url_foto_perfil")
            ),
            friendship_date=friendship.accepted_at or friendship.created_at,
            mutual_friends_count=mutual_friends_count
        )

    @staticmethod
    def to_friend_request_response(
        friendship: FriendshipData,
        requester_info: Dict[str, Any],
        mutual_friends_count: Optional[int] = None
    ) -> FriendRequestResponseDTO:
        return FriendRequestResponseDTO(
            id=friendship.id,
            requester_info=UserInfoDTO(
                id=requester_info.get("id"),
                name=requester_info.get("name") or requester_info.get("nombre"),
                email=requester_info.get("email") or requester_info.get("correo_electronico"),
                profile_photo_url=requester_info.get("profile_photo_url") or requester_info.get("url_foto_perfil")
            ),
            request_date=friendship.created_at,
            mutual_friends_count=mutual_friends_count
        )

    @staticmethod
    def to_friend_suggestion(
        user_info: Dict[str, Any],
        mutual_friends_count: int = 0,
        connection_reason: str = "Usuario recomendado"
    ) -> FriendSuggestionDTO:
        return FriendSuggestionDTO(
            id=user_info.get("id"),
            name=user_info.get("name") or user_info.get("nombre"),
            email=user_info.get("email") or user_info.get("correo_electronico"),
            profile_photo_url=user_info.get("profile_photo_url") or user_info.get("url_foto_perfil"),
            mutual_friends_count=mutual_friends_count,
            connection_reason=connection_reason
        )