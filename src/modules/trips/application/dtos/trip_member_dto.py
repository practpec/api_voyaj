from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from ...domain.trip_member import TripMemberData, TripMemberRole, TripMemberStatus


@dataclass
class InviteMemberDTO:
    user_id: str
    role: TripMemberRole = TripMemberRole.MEMBER
    notes: Optional[str] = None


@dataclass
class UpdateMemberRoleDTO:
    role: TripMemberRole


@dataclass
class HandleInvitationDTO:
    action: str  # "accept" or "reject"


@dataclass
class UpdateMemberNotesDTO:
    notes: Optional[str]


@dataclass
class TripMemberFiltersDTO:
    trip_id: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[TripMemberRole] = None
    status: Optional[TripMemberStatus] = None
    is_active: Optional[bool] = None
    limit: int = 50
    offset: int = 0


@dataclass
class TripMemberResponseDTO:
    id: str
    trip_id: str
    user_id: str
    role: str
    status: str
    notes: Optional[str]
    invited_by: Optional[str]
    invited_at: datetime
    joined_at: Optional[datetime]
    left_at: Optional[datetime]
    user_info: Optional[Dict[str, Any]] = None
    inviter_info: Optional[Dict[str, Any]] = None
    role_label: Optional[str] = None
    status_label: Optional[str] = None


@dataclass
class TripMemberListResponseDTO:
    id: str
    user_info: Dict[str, Any]
    role: str
    status: str
    joined_at: Optional[datetime]
    role_label: str
    can_edit: bool = False
    can_remove: bool = False


@dataclass
class TripMemberStatsDTO:
    total_members: int
    active_members: int
    pending_invitations: int
    admins_count: int
    regular_members_count: int
    recent_joins: int


class TripMemberDTOMapper:
    
    ROLE_LABELS = {
        TripMemberRole.OWNER.value: "Propietario",
        TripMemberRole.ADMIN.value: "Administrador", 
        TripMemberRole.MEMBER.value: "Miembro",
        TripMemberRole.VIEWER.value: "Espectador"
    }
    
    STATUS_LABELS = {
        TripMemberStatus.PENDING.value: "Pendiente",
        TripMemberStatus.ACCEPTED.value: "Aceptado",
        TripMemberStatus.REJECTED.value: "Rechazado",
        TripMemberStatus.LEFT.value: "Abandonó",
        TripMemberStatus.REMOVED.value: "Removido"
    }

    @staticmethod
    def to_member_response(
        member: TripMemberData,
        user_info: Optional[Dict[str, Any]] = None,
        inviter_info: Optional[Dict[str, Any]] = None
    ) -> TripMemberResponseDTO:
        return TripMemberResponseDTO(
            id=member.id,
            trip_id=member.trip_id,
            user_id=member.user_id,
            role=member.role,
            status=member.status,
            notes=member.notes,
            invited_by=member.invited_by,
            invited_at=member.invited_at,
            joined_at=member.joined_at,
            left_at=member.left_at,
            user_info=user_info,
            inviter_info=inviter_info,
            role_label=TripMemberDTOMapper.ROLE_LABELS.get(member.role, member.role),
            status_label=TripMemberDTOMapper.STATUS_LABELS.get(member.status, member.status)
        )

    @staticmethod
    def to_member_list_response(
        member: TripMemberData,
        user_info: Dict[str, Any],
        can_edit: bool = False,
        can_remove: bool = False
    ) -> TripMemberListResponseDTO:
        return TripMemberListResponseDTO(
            id=member.id,
            user_info=user_info,
            role=member.role,
            status=member.status,
            joined_at=member.joined_at,
            role_label=TripMemberDTOMapper.ROLE_LABELS.get(member.role, member.role),
            can_edit=can_edit,
            can_remove=can_remove
        )

    @staticmethod
    def to_member_stats(stats_data: Dict[str, Any]) -> TripMemberStatsDTO:
        return TripMemberStatsDTO(
            total_members=stats_data.get("total_members", 0),
            active_members=stats_data.get("active_members", 0),
            pending_invitations=stats_data.get("pending_invitations", 0),
            admins_count=stats_data.get("admins_count", 0),
            regular_members_count=stats_data.get("regular_members_count", 0),
            recent_joins=stats_data.get("recent_joins", 0)
        )